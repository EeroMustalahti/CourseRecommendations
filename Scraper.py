import time
import datetime

import requests

from Extractor import Extractor


class Scraper:

    uta_curricula_url = 'https://www10.uta.fi/opas/index.htm?uiLang=en'

    uta_url_prefix = 'https://www10.uta.fi/opas/'

    courses_data = {}
    modules_data = {}
    current_faculty = None

    scrape_start_time = None

    extractor = Extractor()

    def __init__(self, data_preserver, status_reporter):
        self.preserver = data_preserver
        self.reporter = status_reporter

    # Methods relating to web scraping courses and study modules data of University of Tampere

    def scrape(self):
        """
        Scrape UTA Curricula Guides to get courses and study modules data and save collected data to files
        """

        # For both courses and modules dataset give one key for the metadata of the dataset
        uta_courses_data = {'dataset_info': {'collected_on': '', 'collected_in': '', 'data_items': 0}}
        uta_modules_data = {'dataset_info': {'collected_on': '', 'collected_in': '', 'data_items': 0}}

        # Collect the datasets
        self.scrape_start_time = time.time()
        self.traverse_curricula()
        data_collected_in = self.get_passed_time()
        self.reporter.uta_scrape_time_span(self.get_passed_time())

        # For both datasets fill the metadata about them
        date_collected_on = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uta_courses_data['dataset_info']['collected_on'] = date_collected_on
        uta_courses_data['dataset_info']['collected_in'] = self.reporter.display_hours_and_minutes(data_collected_in)
        uta_courses_data['dataset_info']['data_items'] = len(self.courses_data)

        uta_modules_data['dataset_info']['collected_on'] = date_collected_on
        uta_modules_data['dataset_info']['collected_in'] = self.reporter.display_hours_and_minutes(data_collected_in)
        uta_modules_data['dataset_info']['data_items'] = len(self.modules_data)

        uta_courses_data.update(self.courses_data)
        uta_modules_data.update(self.modules_data)

        # Save the datasets to files
        self.preserver.save_courses(uta_courses_data)
        self.preserver.save_modules(uta_modules_data)

    def traverse_curricula(self):
        """
        Traverses the UTA Curricula to collect the courses and modules data
        """
        curricula_content = self.get_html(self.uta_curricula_url)
        faculties = self.extractor.get_faculties(curricula_content)
        self.traverse_faculties(faculties)

    def traverse_faculties(self, faculties):
        """
        Traverses the faculties to collect the courses and modules data from each of them
        :param faculties: Dictionary containing HTML division element of each faculty
        """
        for faculty_name, faculty_div in faculties.items():

            self.current_faculty = faculty_name
            self.reporter.scrape_time_passed(self.get_passed_time())
            self.reporter.entering_faculty(faculty_name)

            faculty_links = self.extractor.get_links(faculty_div)
            faculty_links = self.add_uta_url_prefixes(faculty_links)
            self.traverse_faculty_links(faculty_links)

    def traverse_faculty_links(self, links):
        """
        Traverses the links in the faculty to collect modules and courses data inside each of them
        :param links: The links inside the faculty
        """
        for link in links:

            page_content = self.get_html(link)
            education_structure = self.extractor.get_education_structure(page_content)

            if education_structure:
                # If the page has education structure it has collection of programmes
                self.traverse_programme_collection(education_structure)
            elif self.extractor.get_root_element_containing_module_elements(page_content):
                # The page represents one module (possibly with many sub-modules)
                # if it has the root element supposed to contain module info
                self.reporter.entering_module(self.extractor.get_module_name(page_content))
                # Collect the first topmost module's info in specialized way
                self.collect_module_data(page_content, True)
                # If the module has sub-modules they can be collected by using normal method
                self.traverse_programme(page_content, False)
            # Otherwise the page should not have any module or course information

    def traverse_programme_collection(self, education_structure):
        """
        Traverses links inside degree programme's education structure to collect modules and courses data
        inside each of them
        :param education_structure: The element which contains links to programmes
        """
        programme_links = self.extractor.get_links(education_structure)
        programme_links = self.add_uta_url_prefixes(programme_links)

        for programme_link in programme_links:
            programme_content = self.get_html(programme_link)
            self.traverse_programme(programme_content)

    def traverse_programme(self, programme_content, entering_programme=True):
        """
        Traverses page content to obtain modules and courses data
        :param programme_content: The content of the page we will scrape for modules and courses data
        :param entering_programme: Whether we are entering a programme or not in which case we have already
        previously entered to modules page
        """
        programme_name, module_divs = self.extractor.get_programme_info(programme_content)

        if programme_name is None:
            # The programme page does not have content. Ignore it.
            return

        if entering_programme:
            # We have entered a page representing programme, not a module
            self.reporter.scrape_time_passed(self.get_passed_time())
            self.reporter.entering_programme(programme_name)

        self.traverse_modules(module_divs)

    def traverse_modules(self, module_divs):
        """
        Traverses modules to collect their data and their courses data
        :param module_divs: List of elements each containing info about one module
        """
        for module_div in module_divs:
            self.collect_module_data(module_div)

    def collect_module_data(self, module_div, use_special_extraction=False):
        """
        Collect data of individual module and traverse modules courses to collect their data too
        :param module_div: The element containing the module info
        :param use_special_extraction: Whether to use special extraction method to collect such module's data which
        info is not located in typical place. Used for topmost modules in module view pages where part of the info
        is located at the header for example.
        """
        module_id, module_name, module_ects, module_course_ids, parent_module_id, course_links\
            = self.extractor.get_module_data(module_div)\
            if not use_special_extraction else self.extractor.get_module_data_differently(module_div)

        module_data = {
            module_id: {
                'name': module_name,
                'ects': module_ects,
                'courses': module_course_ids,
                'parent': parent_module_id,
                'faculty': self.current_faculty
            }
        }
        self.modules_data.update(module_data)
        self.reporter.module_data_collected(module_data, module_id)

        course_links = self.add_uta_url_prefixes(course_links)
        self.traverse_courses(course_links)

    def traverse_courses(self, course_links):
        """
        Traverse courses to collect their data
        :param course_links: Links to course pages
        """
        for course_link in course_links:
            course_content = self.get_html(course_link)
            self.collect_course_data(course_content)

    def collect_course_data(self, course_content):
        """
        Collect data of individual course. Ignore the course if the course page is broken or the course's
        data has already been collected previously
        :param course_content: the page containing course info
        :return: empty return is done if the course page is broken or course's data has already been collected
        """
        course_id, course_name, course_ects, course_belongs_to_modules \
            = self.extractor.get_course_data(course_content)

        if course_id is None:
            # The course page is broken. Ignore this course.
            self.reporter.cannot_collect_course_data()
            return

        course_data = {
            course_id: {
                'name': course_name,
                'ects': course_ects,
                'belongs_to_modules': course_belongs_to_modules,
                'faculty': self.current_faculty
            }
        }
        if course_id in self.courses_data:
            # This course's data has already been collected
            self.reporter.course_data_already_collected(course_data, course_id)
            return
        self.courses_data.update(course_data)
        self.reporter.course_data_collected(course_data, course_id)

    # Method relating to scraping University of Tampere student's completed courses

    def scrape_student(self, student_faculty):
        """Scrapes student's personal academic transcript to obtain information on completed courses
        and saves the collected study record along with the student's faculty to a file
        :param student_faculty: The faculty of the student whose study record is scraped
        """
        student_data = {'faculty': student_faculty}
        study_record = self.preserver.load_study_record()
        completed_courses = self.extractor.get_completed_courses(study_record)
        student_data.update(completed_courses)

        self.preserver.save_student_data(student_data)

    # Utility methods

    @staticmethod
    def get_html(url):
        """
        Gets HTML content of the web page located in the URL
        :param url: link to a web page
        :return: HTML content of the page
        """
        """Makes request to specified link and retrieves the HTML markup content of it."""
        response = requests.get(url)
        return response.text

    def get_passed_time(self):
        """
        Gets passed time since the start of the dataset scraping process.
        :return: Passed time
        """
        return time.time() - self.scrape_start_time

    def add_uta_url_prefixes(self, links):
        """Adds University of Tampere URL prefixes at the beginning of all links
        to transform relative links to absolute links.
        It is not possible to make requests to relative links,
        therefore this transformation is necessary to make requests to these links.
        :param links: list of relative links
        :return: list of absolute links
        """
        return [self.uta_url_prefix + s for s in links]

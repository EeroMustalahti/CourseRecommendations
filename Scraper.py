import sys
import time
import datetime

import requests

from Extractor import Extractor


class Scraper:

    uta_curricula_url = 'https://www10.uta.fi/opas/index.htm?uiLang=en'

    uta_url_prefix = 'https://www10.uta.fi/opas/'

    student_login = 'https://www10.uta.fi/nettiopsu/login.htm'
    student_academic_transcript = 'https://www10.uta.fi/nettiopsu/suoritukset.htm'

    courses_data = {}
    modules_data = {}
    current_faculty = None

    scrape_start_time = None

    extractor = Extractor()

    def __init__(self, data_preserver, status_reporter):
        self.preserver = data_preserver
        self.reporter = status_reporter

    # Methods relating to web scraping course and study modules data of University of Tampere

    def scrape(self):
        """Scrapes UTA Curricula Guides for course and study module information."""

        uta_courses_data = {'dataset_info': {'collected_on': '', 'collected_in': '', 'data_items': 0}}
        uta_modules_data = {'dataset_info': {'collected_on': '', 'collected_in': '', 'data_items': 0}}

        self.scrape_start_time = time.time()
        self.traverse_curricula()
        data_collected_in = self.get_passed_time()
        self.reporter.uta_scrape_time_span(self.get_passed_time())

        date_collected_on = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uta_courses_data['dataset_info']['collected_on'] = date_collected_on
        uta_courses_data['dataset_info']['collected_in'] = self.reporter.display_hours_and_minutes(data_collected_in)
        uta_courses_data['dataset_info']['data_items'] = len(self.courses_data)

        uta_modules_data['dataset_info']['collected_on'] = date_collected_on
        uta_modules_data['dataset_info']['collected_in'] = self.reporter.display_hours_and_minutes(data_collected_in)
        uta_modules_data['dataset_info']['data_items'] = len(self.modules_data)

        uta_courses_data.update(self.courses_data)
        uta_modules_data.update(self.modules_data)

        self.preserver.save_courses(uta_courses_data)
        self.preserver.save_modules(uta_modules_data)

    def traverse_curricula(self):
        curricula_content = self.get_html(self.uta_curricula_url)
        faculties = self.extractor.get_faculties(curricula_content)
        self.traverse_faculties(faculties)

    def traverse_faculties(self, faculties):
        for faculty_name, faculty_div in faculties.items():
            self.current_faculty = faculty_name
            self.reporter.scrape_time_passed(self.get_passed_time())
            self.reporter.entering_faculty(faculty_name)

            faculty_links = self.extractor.get_links(faculty_div)
            faculty_links = self.add_uta_url_prefixes(faculty_links)
            self.traverse_faculty_links(faculty_links)

            #break  # TESTI VAIN YKSI FACULTY

    def traverse_faculty_links(self, links):
        for link in links:
            page_content = self.get_html(link)
            education_structure = self.extractor.get_education_structure(page_content)

            if education_structure:
                # If the page has education structure it has collection of programmes
                self.traverse_programme_collection(education_structure)
            else:
                # Else the page has information of single programme
                self.traverse_programme(page_content)

            #break  # TESTI VAIN YKSI LINKKI

    def traverse_programme_collection(self, education_structure):
        programme_links = self.extractor.get_links(education_structure)
        programme_links = self.add_uta_url_prefixes(programme_links)

        for programme_link in programme_links:
            programme_content = self.get_html(programme_link)
            self.traverse_programme(programme_content)

            #break  # TESTI VAIN YKSI PROGRAMME

    def traverse_programme(self, programme_content):
        """MERGE THIS METHOD TO traverse_modules?"""
        programme_name, module_divs = self.extractor.get_programme_info(programme_content)
        self.reporter.scrape_time_passed(self.get_passed_time())
        self.reporter.entering_programme(programme_name)

        self.traverse_modules(module_divs)

    def traverse_modules(self, module_divs):
        for module_div in module_divs:
            self.collect_module_data(module_div)

    def collect_module_data(self, module_div):
        module_id, module_name, module_ects, module_course_ids, parent_module_id, course_links\
            = self.extractor.get_module_data(module_div)
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
        for course_link in course_links:
            course_content = self.get_html(course_link)
            self.collect_course_data(course_content)

    def collect_course_data(self, course_content):
        course_id, course_name, course_ects, course_belongs_to_modules \
            = self.extractor.get_course_data(course_content)

        if course_id is None:
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
            self.reporter.course_data_already_collected(course_data, course_id)
            return
        self.courses_data.update(course_data)
        self.reporter.course_data_collected(course_data, course_id)

    # Methods relating to web scraping University of Tampere student's completed courses

    def scrape_student(self):
        """Scrapes student's personal academic transcript to obtain information on completed courses."""
        return []

    # Utility methods

    @staticmethod
    def get_html(url):
        """Makes request to specified link and retrieves the HTML markup content of it."""
        response = requests.get(url)
        return response.text

    def get_passed_time(self):
        """Calculates the passed time since the start of the scraping process."""
        return time.time() - self.scrape_start_time

    def add_uta_url_prefixes(self, links):
        """Adds University of Tampere URL prefixes at the beginning of all links
        to transform relative links to absolute links.
        It is not possible to make requests to relative links,
        therefore this transformation is necessary to make requests to these links."""
        return [self.uta_url_prefix + s for s in links]

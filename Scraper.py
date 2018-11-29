import sys
import time
import datetime
import json

from bs4 import BeautifulSoup
import requests

from Extractor import Extractor
from Preserver import Preserver
from Reporter import Reporter


class Scraper:

    uta_curricula_url = 'https://www10.uta.fi/opas/index.htm?uiLang=en'

    uta_url_prefix = 'https://www10.uta.fi/opas/'

    student_login = 'https://www10.uta.fi/nettiopsu/login.htm'
    student_academic_transcript = 'https://www10.uta.fi/nettiopsu/suoritukset.htm'

    courses_collected = 0
    modules_collected = 0

    extractor = Extractor()
    preserver = Preserver()
    reporter = Reporter()

    def __init__(self):
        self.scrape_start_time = None

    # Methods relating to web scraping course and study modules data of University of Tampere

    def scrape(self):
        """Scrapes UTA Curricula Guides for course and study module information."""

        uta_courses_data = {'dataset_info': {'collected_on': '', 'collected_in': '', 'data_items': 0}}
        uta_modules_data = {'dataset_info': {'collected_on': '', 'collected_in': '', 'data_items': 0}}

        self.scrape_start_time = time.time()
        courses_data, modules_data = self.traverse_curricula()
        data_collected_in = self.get_passed_time()
        self.reporter.uta_scrape_time_span(self.get_passed_time())

        date_collected_on = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        uta_courses_data['dataset_info']['collected_on'] = date_collected_on
        uta_courses_data['dataset_info']['collected_in'] = self.reporter.display_hours_and_minutes(data_collected_in)
        uta_courses_data['dataset_info']['data_items'] = self.courses_collected

        uta_modules_data['dataset_info']['collected_on'] = date_collected_on
        uta_modules_data['dataset_info']['collected_in'] = self.reporter.display_hours_and_minutes(data_collected_in)
        uta_modules_data['dataset_info']['data_items'] = self.modules_collected

        print('courses_data len: ' + str(len(courses_data)))
        print('modules_data len: ' + str(len(modules_data)))

        uta_courses_data.update(courses_data)
        uta_modules_data.update(modules_data)

        self.preserver.save_courses(uta_courses_data)
        self.preserver.save_modules(uta_modules_data)

    def traverse_curricula(self):
        curricula_content = self.get_html(self.uta_curricula_url)
        faculties = self.extractor.get_faculties(curricula_content)
        courses_data, modules_data = self.traverse_faculties(faculties)

        return courses_data, modules_data

    def traverse_faculties(self, faculties):
        courses_data = {}
        modules_data = {}

        for faculty_name, faculty_div in faculties.items():
            self.reporter.scrape_time_passed(self.get_passed_time())
            self.reporter.entering_faculty(faculty_name)
            faculty_links = self.extractor.get_links(faculty_div)

            faculty_links = [self.uta_url_prefix + s for s in faculty_links]  # Add missing URL prefixes to links

            faculty_courses_data, faculty_modules_data = self.traverse_faculty_links(faculty_links)
            courses_data.update(faculty_courses_data)
            modules_data.update(faculty_modules_data)

            break  # TESTI VAIN YKSI FACULTY

        return courses_data, modules_data

    def traverse_faculty_links(self, links):
        faculty_courses_data = {}
        faculty_modules_data = {}

        for link in links:
            page_content = self.get_html(link)
            education_structure = self.extractor.get_education_structure(page_content)

            # collected_courses_data = {}
            # collected_modules_data = {}
            if education_structure:
                # If the page has education structure it has collection of programmes
                collected_courses_data, collected_modules_data = self.traverse_programme_collection(education_structure)
            else:
                # Else the page has information of single programme
                collected_courses_data, collected_modules_data = self.traverse_programme(page_content)
            faculty_courses_data.update(collected_courses_data)
            faculty_modules_data.update(collected_modules_data)

            break  # TESTI VAIN YKSI LINKKI

        return faculty_courses_data, faculty_modules_data

    def traverse_programme_collection(self, education_structure):
        programme_links = self.extractor.get_links(education_structure)
        programme_links = [self.uta_url_prefix + s for s in programme_links]  # Add missing URL prefixes to links

        collected_courses_data = {}
        collected_modules_data = {}
        for programme_link in programme_links:
            programme_content = self.get_html(programme_link)
            programme_courses_data, programme_modules_data = self.traverse_programme(programme_content)
            collected_courses_data.update(programme_courses_data)
            collected_modules_data.update(programme_modules_data)

            break  # TESTI VAIN YKSI PROGRAMME

        return collected_courses_data, collected_modules_data

    def traverse_programme(self, programme_content):
        """MERGE THIS METHOD TO traverse_modules?"""
        # Change to extract only module links, courses will be traversed later in each module
        programme_name, module_divs = self.extractor.get_programme_info(programme_content)
        self.reporter.scrape_time_passed(self.get_passed_time())
        self.reporter.entering_programme(programme_name)

        programme_courses_data, programme_modules_data = self.traverse_modules(module_divs)

        return programme_courses_data, programme_modules_data

    def traverse_modules(self, module_divs):
        programme_courses_data = {}
        programme_modules_data = {}
        for module_div in module_divs:
            module_courses_data, module_data = self.collect_module_data(module_div)
            programme_courses_data.update(module_courses_data)
            programme_modules_data.update(module_data)

        return programme_courses_data, programme_modules_data

    def collect_module_data(self, module_div):
        module_id, module_name, module_ects, module_course_ids, parent_module_id, course_links\
            = self.extractor.get_module_data(module_div)
        module_data = {
            module_id: {
                'name': module_name,
                'ects': module_ects,
                'courses': module_course_ids,
                'parent': parent_module_id
            }
        }
        self.reporter.module_data_collected(module_data, module_id)
        self.modules_collected += 1

        course_links = self.add_uta_url_prefixes(course_links)
        module_courses_data = self.traverse_courses(course_links)

        return module_courses_data, module_data

    def traverse_courses(self, course_links):
        module_courses_data = {}
        for course_link in course_links:
            course_content = self.get_html(course_link)
            module_course_data = self.collect_course_data(course_content)
            module_courses_data.update(module_course_data)

        return module_courses_data

    def collect_course_data(self, course_content):
        course_id, course_name, course_ects, course_belongs_to_modules \
            = self.extractor.get_course_data(course_content)
        course_data = {
            course_id: {
                'name': course_name,
                'ects': course_ects,
                'belongs_to_modules': course_belongs_to_modules
            }
        }
        self.reporter.course_data_collected(course_data, course_id)
        self.courses_collected += 1
        return course_data

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

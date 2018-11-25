import sys
import time
import json

from bs4 import BeautifulSoup
import requests

from Extractor import Extractor
from Preserver import Preserver
from Reporter import Reporter


class Scraper:

    uta_curricula_url = 'https://www10.uta.fi/opas/index.htm?uiLang=en'

    scrape_url = 'https://www10.uta.fi/opas/koulutus.htm?opsId=162&uiLang=en&lang=en&lvv=2018&koulid=403'
    small_scrape_url = 'https://www10.uta.fi/opas/koulutus.htm?opsId=162&uiLang=en&lang=en&lvv=2018&koulid=403'

    url_prefix = 'https://www10.uta.fi/opas/'
    uta_url_prefix = 'https://www10.uta.fi/opas/'

    course_htmls_file = 'CourseHtmls.json'
    courses_file = 'courses.json'
    modules_file = 'modules.json'

    student_login = 'https://www10.uta.fi/nettiopsu/login.htm'
    student_academic_transcript = 'https://www10.uta.fi/nettiopsu/suoritukset.htm'

    extractor = Extractor()
    preserver = Preserver()
    reporter = Reporter()

    def __init__(self):
        pass

    # Methods relating to web scraping course and study modules data of University of Tampere

    def scrape(self):
        """Scrapes UTA Curricula Guides for course and study module information."""

        start_time = time.time()
        courses_data, modules_data = self.traverse_curricula()
        end_time = time.time()
        self.reporter.uta_scrape_time_span(end_time - start_time)

        self.preserver.save_courses(courses_data)
        self.preserver.save_modules(modules_data)

    def traverse_curricula(self):
        curricula_content = self.get_html(self.uta_curricula_url)
        faculties = self.extractor.get_faculties(curricula_content)
        courses_data, modules_data = self.traverse_faculties(faculties)

        return courses_data, modules_data

    def traverse_faculties(self, faculties):
        courses_data = {}
        modules_data = {}

        for faculty_name, faculty_div in faculties.items():
            self.reporter.entering_faculty(faculty_name)
            faculty_links = self.extractor.get_links_of_faculty(faculty_div)

            # Add missing URL prefix at the beginning of each link
            faculty_links = [self.uta_url_prefix + s for s in faculty_links]

            faculty_courses_data, faculty_modules_data = self.traverse_faculty_links(faculty_links)
            courses_data.update(faculty_courses_data)
            modules_data.update(faculty_modules_data)

        return courses_data, modules_data

    def traverse_faculty_links(self, links):
        faculty_courses_data = {}
        faculty_modules_data = {}

        for link in links:
            page_content = self.get_html(link)
            education_structure = self.extractor.get_education_structure(page_content)

            if education_structure:
                # If the page has education structure it has collection of programmes
                self.traverse_programme_collection(education_structure)
            else:
                # Else the page has information of single programme
                self.traverse_programme()

        return faculty_courses_data, faculty_modules_data

    def traverse_programme_collection(self, education_stucture):
        sys.exit('To be implemented')
        pass

    def traverse_programme(self):
        sys.exit('To be implemented')
        pass

    def small_scrape(self):
        """Scrapes only Degree Programme in Computer Sciences for course and study module information.."""
        pass

    # Methods relating to web scraping Univerisy of Tampere student's completed courses

    def scrape_student(self):
        """Scrapes student's personal academic transcript to obtain information on completed courses."""
        pass

    # Utility methods

    @staticmethod
    def get_html(url):
        response = requests.get(url)
        return response.text

    def get_courses_html(self):
        """TO BE REMOVED"""
        course_htmls = {}

        r = requests.get(self.scrape_url)
        data = r.text
        html = BeautifulSoup(data, 'html.parser')
        # Ota linkit jotka johtaa tutkintoihin
        education_structure = html.find('div', {'class': 'koulutus_rakenne'})
        programmes = education_structure.findChildren('a')
        programme_urls = []

        # Lasketaan kuinka paljon aikaa menee kurssien HTML:ien hakemiseen
        start_time = time.time()

        programme_counter = 1
        for a in programmes:
            programme_urls.append(a.get('href'))
        for programme_url in programme_urls:
            print('Programme ' + str(programme_counter))
            programme_counter += 1

            r = requests.get(self.url_prefix + programme_url)
            data = r.text
            programme_html = BeautifulSoup(data, 'html.parser')

            course_divs = programme_html.find_all('div', {'class': 'tutrak_subElement_oj'})
            course_as = []
            for course_div in course_divs:
                course_as.append(course_div.findChild('a'))
            course_urls = []
            for course_a in course_as:
                course_urls.append(course_a.get('href'))

            course_counter = 1
            for course_url in course_urls:
                print('course ' + str(course_counter))
                course_counter += 1

                r = requests.get(self.url_prefix + course_url)
                data = r.text
                course_html = BeautifulSoup(data, 'html.parser')
                #print(course_html)

                # Käytetään avaimena kurssin koodia ja arvona kurssin HTML:ää
                div_elem = course_html.find("div", {"class": "department_header"})
                course_code = div_elem.text.split()[0].strip()
                course_htmls[course_code] = str(course_html)

        # Tarkistetaan suoritukseen mennyt aika
        end_time = time.time()
        print('Time to fetch courses\' htmls: ' + str(end_time - start_time))
        print('Number of courses: ' + str(len(course_htmls)))

        # Save course htmls as json
        with open(self.course_htmls_file, 'w') as f:
            json.dump(course_htmls, f)

        return course_htmls

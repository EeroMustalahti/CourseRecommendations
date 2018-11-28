import sys
import json

from bs4 import BeautifulSoup

from Reporter import Reporter


class Extractor:

    parser = 'html.parser'

    course_htmls_file = 'CourseHtmls.json'

    def __init__(self):
        pass

    def get_faculties(self, curricula_content):
        curricula_soup = self.get_soup(curricula_content)

        faculties = {}
        faculty_divs = curricula_soup.find_all('div', {'class': 'frontpage_unit_content'})

        for faculty_div in faculty_divs:
            faculty_a = faculty_div.parent.find('div', {'class': 'frontpage_header'}).find('a')
            faculty_name_stripped = faculty_a.text.strip()
            faculty_name = ' '.join(faculty_name_stripped.split())  # Shorten huge gap between name and year span

            faculties[faculty_name] = faculty_div

        return faculties

    def get_education_structure(self, page_content):
        page_soup = self.get_soup(page_content)
        education_structure = page_soup.find('div', {'class': 'koulutus_rakenne'})
        return education_structure

    def get_programme_info(self, programme_content):
        programme_soup = self.get_soup(programme_content)
        programme_name = programme_soup.find('h3').text.strip()
        module_divs = programme_soup.select('div[class*="tutrak_okokonaisuus"]')  # 'div[class*="listing-col-"]'

        return programme_name, module_divs

    def get_module_data(self, module_div):
        name = module_div.find('a').text.strip()
        sys.exit(name)
        return 'id', 'name', 0, [], 'parent', []

    def get_course_data(self, course_content):
        return 'id', 'name', 0, []

    @staticmethod
    def get_links(element):
        links = []
        for anchor in element.find_all('a'):
            links.append(anchor.get('href'))
        return links

    # Utility methods

    def get_soup(self, page_content):
        return BeautifulSoup(page_content, self.parser)

    def get_courses_data(self):
        """TO BE REMOVED"""
        courses_data = {}
        with open(self.course_htmls_file) as f:
            courses_htmls = json.load(f)

        for key, value in courses_htmls.items():
            courses_htmls[key] = BeautifulSoup(value, 'html.parser')

        # Start to extract data of each course
        for key, course_html in courses_htmls.items():
            study_modules = []
            h2_elem = course_html.find('h2', text='Belongs to following study modules')
            div_elem = h2_elem.find_next_sibling('div')
            for link in div_elem('a'):
                study_modules.append(link.string)
            courses_data[key] = study_modules

        # Check if worked
        #for key, value in courses_data.items():
        #    print(key + ':')
        #    for item in value:
        #        print('   ' + item)

        return courses_data

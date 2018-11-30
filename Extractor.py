import sys
import re

from bs4 import BeautifulSoup


class Extractor:

    parser = 'html.parser'

    def __init__(self):
        pass

    def get_faculties(self, curricula_content):
        curricula_soup = self.get_soup(curricula_content)

        faculties = {}
        faculty_divs = curricula_soup.find_all('div', {'class': 'frontpage_unit_content'})

        for faculty_div in faculty_divs:
            faculty_a = faculty_div.parent.find('div', {'class': 'frontpage_header'}).find('a')
            faculty_name = faculty_a.text.rsplit(maxsplit=1)[0].strip()

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

    @staticmethod
    def get_module_data(module_div):
        id_ = module_div['id'].split('_')[1].strip()
        name = module_div.select_one('a').text.strip()

        # Not all courses have specified ECTS
        ects = ''.join(c for c in module_div.select_one('a').next_sibling if c.isdigit())
        if ects.isdigit():
            ects = int(ects)
        else:
            ects = None

        course_ids = []
        course_links = []
        childs_div = module_div.select_one('div[class*="lapset"]')
        if childs_div:
            course_divs = childs_div.find_all('div', {'class': 'tutrak_subElement_oj'}, recursive=False)
            for course_div in course_divs:
                course_ids.append(course_div.select_one('a').previous_sibling.strip())
                course_links.append(course_div.select_one('a').get('href'))

        parent_module_id = None
        if module_div.parent.has_attr('id'):
            parent_module_id = module_div.parent['id'].split('_')[1].strip()

        return id_, name, ects, course_ids, parent_module_id, course_links

    def get_course_data(self, course_content):
        course_soup = self.get_soup(course_content)
        header_div = course_soup.find('div', {'class': 'department_header'})

        # Some course pages no not work, their data cannot be collected (example: KKRUTEK)
        # Hotfix
        if header_div is None:
            return None, None, None, None

        header_strings = header_div.text.split(maxsplit=1)
        id_ = header_strings[0].strip()

        header_strings = header_strings[1].split('\r', maxsplit=1)
        name = header_strings[0].strip()

        header_strings = header_strings[1].split()
        ects = None
        # Not all courses have ECTS amount (example: VENP0)
        if header_strings:
            ects = header_strings[0].strip()
            if '–' in ects:
                # If course has varying ECTS amount take only note of the minimum amount
                ects = int(ects.split('–')[0].strip())
            else:
                ects = int(ects)

        belongs_to_modules_div = course_soup.find('h2', text='Belongs to following study modules').find_next_sibling('div')
        module_ids = []
        for anchor in belongs_to_modules_div('a'):
            href = anchor.get('href')
            module_id = re.search('rid=(.+?)&', href).group(1)
            module_ids.append(module_id)

        return id_, name, ects, module_ids

    @staticmethod
    def get_links(element):
        links = []
        for anchor in element.find_all('a'):
            links.append(anchor.get('href'))
        return links

    # Utility methods

    def get_soup(self, page_content):
        return BeautifulSoup(page_content, self.parser)

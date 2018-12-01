import sys
import re

from bs4 import BeautifulSoup


class Extractor:

    parser = 'html.parser'

    filter_name = ''

    def __init__(self):
        pass

    def get_faculties(self, curricula_content):
        curricula_soup = self.get_soup(curricula_content)

        faculties = {}
        faculty_divs = curricula_soup.find_all('div', {'class': 'frontpage_unit_content'})

        for faculty_div in faculty_divs:
            faculty_a = faculty_div.parent.find('div', {'class': 'frontpage_header'}).find('a')
            faculty_name = faculty_a.text.rsplit(maxsplit=1)[0].strip()

            # Add only names which have word 'Faculty' in them, they should be "actual" faculties
            if 'Faculty' in faculty_name:
                faculties[faculty_name] = faculty_div

        return faculties

    def get_education_structure(self, page_content):
        page_soup = self.get_soup(page_content)
        education_structure = page_soup.find('div', {'class': 'koulutus_rakenne'})
        return education_structure

    def get_programme_info(self, programme_content):
        programme_soup = self.get_soup(programme_content)
        programme_name = programme_soup.find('h3')

        # Hotfix: sometimes programme has no content. Skip it then
        # (example: Nuorisotyön ja nuorisotutkimuksen maisteriohjelma 2015-2017)
        if programme_name is None:
            return None, None

        programme_name = programme_name.text.strip()

        module_divs = programme_soup.select('div[class*="tutrak_okokonaisuus"]')
        return programme_name, module_divs

    # Hotfix: get module name to report what module we are entering
    def get_module_name(self, page):
        soup = self.get_soup(page)
        return soup.select_one('h3').text.strip()

    # Hotfix: find out is current page Degree Programme where modules are listed
    # (NOTE): Programme pages are not landing pages
    def check_if_programme_page(self, page_content):
        page_soup = self.get_soup(page_content)
        module_div = page_soup.select_one('div[class*="tutrak_okokonaisuus"]')
        if module_div:
            return True
        return False

    # Hotfix: is current page module page. Checking root should be enough (checks for e.g. collection already made)
    def get_root_element(self, page_content):
        page_soup = self.get_soup(page_content)
        return page_soup.select_one('div[class="tutrak_elem_current_root"]')

    # Hotfix: filter to get right link from bread crumbds
    def has_name(self, tag):
        return tag.name == 'a' and self.filter_name in tag.text

    # Hotfix: module data getter for case when page has only single module info. Gets the module data of upmost module
    def get_module_data_differently(self, module_page):
        module_soup = self.get_soup(module_page)

        name = module_soup.select_one('h3').text.strip()

        self.filter_name = name  #Hotfix
        href_where_id = module_soup.select_one('div[id="murupolku"]').find(self.has_name).get('href')
        id_ = re.search('rid=(.+?)&', href_where_id).group(1)

        # Hotfix: take only note of right side of ',' (some modules have year span included in them)
        header_parts = module_soup.find('div', {'class': "department_header"}).text.rsplit(',', maxsplit=1)
        ects = None  # Not all courses have specified ECTS
        if len(header_parts) > 1:
            ects_text = header_parts[1]
            ects_text = ''.join(c for c in ects_text if (c.isdigit() or c == '–'))
            if '–' in ects_text:
                # If module has varying ECTS amount take only note of the minimum amount
                ects = int(ects_text.split('–')[0].strip())
            elif ects_text.isdigit():
                ects = int(ects_text)

        course_ids = []
        course_links = []
        childs_div = module_soup.select_one('div[class="tutrak_elem_current_root"]')
        if childs_div:
            course_divs = childs_div.find_all('div', {'class': 'tutrak_subElement_oj'}, recursive=False)
            for course_div in course_divs:
                course_ids.append(course_div.select_one('a').previous_sibling.strip())
                course_links.append(course_div.select_one('a').get('href'))

        parent_module_id = None

        return id_, name, ects, course_ids, parent_module_id, course_links

    @staticmethod
    def get_module_data(module_div):
        id_ = module_div['id'].split('_')[1].strip()
        name = module_div.select_one('a').text.strip()

        ects = ''.join(c for c in module_div.select_one('a').next_sibling if (c.isdigit() or c == '–'))
        if '–' in ects:
            # If module has varying ECTS amount take only note of the minimum amount
            ects = int(ects.split('–')[0].strip())
        elif ects.isdigit():
            ects = int(ects)
        else:
            # Not all courses have specified ECTS
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

        belongs_to_modules_div = course_soup.find('h2', id='parents').find_next_sibling('div')
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

    # Methods extracting data about student

    def get_completed_courses(self, page):
        soup = self.get_soup(page)
        rows = soup.select_one('div[id="suortapa1_content"]').select('tr')

        student_courses = {}
        for row in rows:
            if row.select_one('td') is None:
                continue
            course_id = row.select_one('td').text.strip()
            obtained_ects = int(row.select('td')[2:][0].text.strip())
            student_courses[course_id] = {'ects': obtained_ects}

        return student_courses

    def get_hidden_fields(self, page):
        soup = self.get_soup(page)

        warn_input = soup.select_one('input[name="warn"]')
        warn = warn_input.get('value')

        lt_input = soup.select_one('input[name="lt"]')
        lt = lt_input.get('value')

        exe_input = soup.select_one('input[name="execution"]')
        exe = exe_input.get('value')

        _eventId_input = soup.select_one('input[name="_eventId"]')
        _eventId = _eventId_input.get('value')

        submit_input = soup.select_one('input[name="submit"]')
        submit = submit_input.get('value')

        reset_input = soup.select_one('input[name="reset"]')
        reset = reset_input.get('value')

        return warn, lt, exe, _eventId, submit, reset

    def get_student_faculty(self, page_content):
        page_soup = self.get_soup(page_content)
        print(page_soup.select_one('h2').text)

    # Utility methods

    def get_soup(self, page_content):
        return BeautifulSoup(page_content, self.parser)

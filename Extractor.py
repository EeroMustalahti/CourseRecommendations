import re

from bs4 import BeautifulSoup


class Extractor:

    parser = 'html.parser'

    filter_name = ''  # Used in custom filter to find anchor element which contains this module's name

    # Methods extracting elements during scraping process to navigate to module and course pages
    # and extracting data about courses and modules

    def get_faculties(self, curricula_content):
        """
        Gets faculty names and the division elements containing links to degree programmes and modules of a faculty
        :param curricula_content: The UTA Curricula Guides main page content
        :return: Dictionary with faculty name as key and faculty's element containing its links as value
        """
        curricula_soup = self.get_soup(curricula_content)

        faculties = {}
        faculty_divs = curricula_soup.find_all('div', {'class': 'frontpage_unit_content'})

        for faculty_div in faculty_divs:
            # Extract the faculty's name from its link
            faculty_a = faculty_div.parent.find('div', {'class': 'frontpage_header'}).find('a')
            faculty_name = faculty_a.text.rsplit(maxsplit=1)[0].strip()

            if 'Faculty' in faculty_name:
                # Add only names which have word 'Faculty' in them, they should be "actual" faculties
                faculties[faculty_name] = faculty_div

        return faculties

    def get_education_structure(self, page_content):
        """
        Get the education structure element
        :param page_content: Content of the page
        :return: The education structure element or None if the page does not contain educations structure
        """
        page_soup = self.get_soup(page_content)
        education_structure = page_soup.find('div', {'class': 'koulutus_rakenne'})
        return education_structure

    def get_programme_info(self, programme_content):
        """
        Gets the name of the programme and module elements belonging to the programme
        :param programme_content: The content of the programme page
        :return: or None if the programme does not have any content
        """
        programme_soup = self.get_soup(programme_content)
        programme_name = programme_soup.find('h3')

        if programme_name is None:
            # Sometimes the programme page does not have any content. Ignore it then.
            return None, None

        programme_name = programme_name.text.strip()

        module_divs = programme_soup.select('div[class*="tutrak_okokonaisuus"]')
        return programme_name, module_divs

    def get_module_name(self, page):
        """
        Gets the name of the topmost module we have entered
        :param page: Content of the page
        :return: The name of the module
        """
        soup = self.get_soup(page)
        return soup.select_one('h3').text.strip()

    def get_root_element_containing_module_elements(self, page_content):
        """
        Get root element which contains module elements
        :param page_content: The content of the page
        :return: The root element or None if the page does not contain the root element
        """
        page_soup = self.get_soup(page_content)
        return page_soup.select_one('div[class="tutrak_elem_current_root"]')

    def has_name(self, tag):
        """
        Custom filter for testing whether the tag is the one we are looking for
        :param tag: The tag which is tested whether it is anchor element and contains the module's name in its text
        :return: Whether the tag is the one we are looking for
        """
        return tag.name == 'a' and self.filter_name in tag.text

    def get_module_data_differently(self, module_page):
        """
        Extract module data in specialized way. This data extraction method is done to modules which are
        topmost modules in module pages where we land when entering a link inside the faculty
        :param module_page: The content of the module page
        :return: ID, name, credits, list of course IDs the module contains, parent module and links
        to the pages of the courses the module contains.
        """
        module_soup = self.get_soup(module_page)

        name = module_soup.select_one('h3').text.strip()  # This module's name mus be extracted from header

        self.filter_name = name
        # The ID of the module must be extracted from a breadcrumb link.
        # Custom filer is needed to get the right breadcrumb link.
        href_where_id = module_soup.select_one('div[id="murupolku"]').find(self.has_name).get('href')
        id_ = re.search('rid=(.+?)&', href_where_id).group(1)

        # Take only note of right side of ','
        # (some modules have year span included in them. Do not include that in the name)
        header_parts = module_soup.find('div', {'class': "department_header"}).text.rsplit(',', maxsplit=1)
        ects = None  # Not all modules have specified ECTS
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

        parent_module_id = None  # The topmost module cannot have a parent

        return id_, name, ects, course_ids, parent_module_id, course_links

    @staticmethod
    def get_module_data(module_div):
        """
        Extracts module's data
        :param module_div: The element from which to collect the module's data
        :return: ID, name, credits, list of course IDs the module contains, parent module and links
        to the pages of the courses the module contains.
        """
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
        """
        Extracts course data
        :param course_content: The course page containing course info
        :return: ID, name, credits, list of IDs of the modules where this course belongs
        """
        course_soup = self.get_soup(course_content)
        header_div = course_soup.find('div', {'class': 'department_header'})

        if header_div is None:
            # Some course pages no not work, their data cannot be collected
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

    # Method extracting data about student

    def get_completed_courses(self, page):
        """

        :param page:
        :return: Dictionary with course ID as key and a dictionary value with
        ects as key and obtained credit amount by the student as value
        """
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

    # Utility methods

    @staticmethod
    def get_links(element):
        """
        Gets links inside the HTML element
        :param element: The element from which the links are extracted
        :return: List of links
        """
        links = []
        for anchor in element.find_all('a'):
            links.append(anchor.get('href'))
        return links

    def get_soup(self, page_content):
        """
        Converts HTML content to a "soup" form which can be used to navigate the content
        :param page_content: HTML content of a web page
        :return: navigateable form of the HTML content
        """
        return BeautifulSoup(page_content, self.parser)

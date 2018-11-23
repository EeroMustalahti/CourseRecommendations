import sys
import time
import json

from bs4 import BeautifulSoup
import requests


class Extractor:

    uta_curricula_url = 'https://www10.uta.fi/opas/index.htm?uiLang=en'
    # Kokeillaan ensin vain tietojenkäsittelytieteiden tutkinto-ohjelman kursseja
    scrape_url = 'https://www10.uta.fi/opas/koulutus.htm?opsId=162&uiLang=en&lang=en&lvv=2018&koulid=403'
    url_prefix = 'https://www10.uta.fi/opas/'
    course_htmls_file = 'CourseHtmls.json'

    def __init__(self):
        """"""

    def get_courses_data(self):
        """Gets courses data from HTMLs"""
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

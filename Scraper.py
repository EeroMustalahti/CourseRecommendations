import sys
import time
import json

from bs4 import BeautifulSoup
import requests


class Scraper:

    uta_curricula_url = 'https://www10.uta.fi/opas/index.htm?uiLang=en'
    # Kokeillaan ensin vain tietojenkäsittelytieteiden tutkinto-ohjelman kursseja
    scrape_url = 'https://www10.uta.fi/opas/koulutus.htm?opsId=162&uiLang=en&lang=en&lvv=2018&koulid=403'
    url_prefix = 'https://www10.uta.fi/opas/'
    course_htmls_file = 'CourseHtmls.json'

    def __init__(self):
        """"""

    def get_courses_html(self):
        """Gets HTML markup of courses."""
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
                course_htmls[course_code] = course_html

        # Tarkistetaan suoritukseen mennyt aika
        end_time = time.time()
        print('Time to fetch courses\' htmls: ' + str(end_time - start_time))
        print('Number of courses: ' + str(len(course_htmls)))
        for key, value in course_htmls.items():
            print(key)
        # Save course htmls as json
        #with open(self.course_htmls_file, 'w') as f:
        #    json.dump(course_htmls, f)

        return course_htmls


    def remove_duplicates(self):
        """Removes duplicate HTMLs."""

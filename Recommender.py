import sys
import time
import json

from bs4 import BeautifulSoup
import requests


class Recommender:

    uta_curricula_url = 'https://www10.uta.fi/opas/index.htm?uiLang=en'
    # Kokeillaan ensin vain tietojenkäsittelytieteiden tutkinto-ohjelman kursseja
    scrape_url = 'https://www10.uta.fi/opas/koulutus.htm?opsId=162&uiLang=en&lang=en&lvv=2018&koulid=403'
    url_prefix = 'https://www10.uta.fi/opas/'
    course_htmls_file = 'CourseHtmls.json'

    def __init__(self):
        """"""

    def recommend(self, passed_courses, courses_data):
        """Recommends courses."""
        courses_score = {}
        for passed_course in passed_courses:
            passed_course_data = courses_data[passed_course]
            other_courses = []
            for module in passed_course_data:
                other_courses_in_module = []
                for course, modules in courses_data.items():
                    if module in modules:
                        other_courses_in_module.append(course)
                other_courses.append(other_courses_in_module)

            for course_list in other_courses:
                for course in course_list:
                    if course != passed_course:
                        courses_score[course] = 1
        for key, value in courses_score.items():
            print(key + ': ' + str(1))
            #course_key = list(courses_data.keys())[list(courses_data.values()).index(module)]
            #print(course_key)

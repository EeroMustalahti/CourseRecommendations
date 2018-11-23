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


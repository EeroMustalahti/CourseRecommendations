import sys
import json

from Scraper import Scraper
from Extractor import Extractor
from Recommender import Recommender

# Ota kurssimoduuleissa huomioon mihin tiedekuntaan kuuluu (esim. faculty of natural sciences)
# suosi kursseja jotka kuuluu oman tiedekunnan moduuleihin

def main():
    # Procedure to make course recommendations using content-based filtering

    scraper = Scraper()
    extractor = Extractor()
    recommender = Recommender()

    # Scrape UTA website to get HTML markup of course pages
    if sys.argv[1] == 'get':
        courses_htmls = scraper.get_courses_html()

    # Extract attributes from each course's HTML markup and make data structure containing course infos
    courses_data = extractor.get_courses_data()

    # Scrape student's NettiOpsu study record page to get HTML markup

    # Extract course IDs from HTML markup and make data structure containing ID's of passed courses
    passed_courses = ['TIEP1']

    # Recommend courses to student
    recommender.recommend(passed_courses, courses_data)


if __name__ == "__main__":
    main()

import sys
import json

from Scraper import Scraper
from Extractor import Extractor
from Recommender import Recommender


def main():
    # Procedure to make course recommendations using content-based filtering

    scraper = Scraper()
    extractor = Extractor()
    recommender = Recommender()

    # Scrape UTA website to get HTML markup of course pages
    courses_htmls = scraper.get_courses_html()

    #with open('CourseHtmls.json') as f:
    #    a = json.load(f)
    # Extract attributes from each course's HTML markup and make data structure containing course infos

    # Scrape student's NettiOpsu study record page to get HTML markup

    # Extract course IDs from HTML markup and make data structure containing ID's of passed courses

    # Make data structure containing study modules and what courses belong to them

    # Make data structure containing info of what


if __name__ == "__main__":
    main()

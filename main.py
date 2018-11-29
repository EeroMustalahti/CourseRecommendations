import sys

from Scraper import Scraper
from Recommender import Recommender


def main():
    # Procedure to make course recommendations using content-based filtering

    # Commands to configure behaviour
    scrape_uta = sys.argv[1]  # Scrape website for courses and modules (y = yes)
    scrape_student = sys.argv[2]  # Scrape students personal study record (y = yes, f = use fake student data)
    execute_recommendation = sys.argv[3]  # Make recommendations (y = yes)

    web_scraper = Scraper()
    course_recommender = Recommender()

    if scrape_uta == 'y':
        # Scrape UTA courses and study modules data
        web_scraper.scrape()

    student_completed_courses = []
    if scrape_student == 'y':
        # Scrape UTA student's personal study record to obtain completed courses
        student_completed_courses = Scraper().scrape_student()
    elif scrape_student == 'f':
        # Make recommendations to a fake student with predetermined completed courses
        student_completed_courses = course_recommender.get_fake_student_completed_courses()

    # Recommend courses to student
    if execute_recommendation == 'y':
        course_recommender.recommend(student_completed_courses)


if __name__ == "__main__":
    main()

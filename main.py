import sys
import time

from CommandReader import CommandReader
from Scraper import Scraper
from Recommender import Recommender
from Reporter import Reporter
from Preserver import Preserver


def main():

    start_time = time.time()

    scrape_data, student_data, student_faculty, execute_recommendation, logging_amount, logging_amount_to_file\
        = CommandReader().get_user_input(sys.argv)

    status_reporter = Reporter(logging_amount, logging_amount_to_file)
    data_preserver = Preserver(status_reporter)
    status_reporter.preserver = data_preserver
    status_reporter.delete_old_logfile()

    web_scraper = Scraper(data_preserver, status_reporter)
    course_recommender = Recommender(data_preserver, status_reporter)

    if scrape_data:
        # Scrape UTA courses and study modules data
        web_scraper.scrape()

    real_student = True
    if student_data == 'y':
        # Scrape UTA student's personal study record to obtain completed courses
        web_scraper.scrape_student(student_faculty)
    else:
        # Make recommendations to a fake student with predetermined completed courses
        real_student = False
        course_recommender.get_fake_student_completed_courses(student_data)

    # Recommend courses to student
    if execute_recommendation:
        course_recommender.recommend(real_student)

    status_reporter.program_execution_time(time.time() - start_time)


if __name__ == "__main__":
    main()

import sys
import time

from Scraper import Scraper
from Recommender import Recommender
from Reporter import Reporter
from Preserver import Preserver


def main():

    start_time = time.time()
    # Procedure to make course recommendations using content-based filtering

    # Commands to configure behaviour
    scrape_uta = sys.argv[1]  # Scrape website for courses and modules (y = yes)
    scrape_student = sys.argv[2]  # Scrape students personal study record (y = yes, f = use fake student data)
    execute_recommendation = sys.argv[3]  # Make recommendations (y = yes)
    # How much logging is done to trace the execution of scrape process
    # (f = full, i = all except modules' courses and modules where course belong,
    # any other = all except when individual module or course data is collected)
    logging_amount = sys.argv[4]
    # How much logging is saved to a file. Same command options as above
    logging_amount_to_file = sys.argv[5]

    status_reporter = Reporter(logging_amount, logging_amount_to_file)
    data_preserver = Preserver(status_reporter)
    status_reporter.preserver = data_preserver
    status_reporter.delete_old_logfile()

    web_scraper = Scraper(data_preserver, status_reporter)
    course_recommender = Recommender(data_preserver, status_reporter)

    if scrape_uta == 'y':
        # Scrape UTA courses and study modules data
        web_scraper.scrape()

    student_completed_courses = []
    if scrape_student == 'y':
        # Scrape UTA student's personal study record to obtain completed courses
        student_completed_courses = web_scraper.scrape_student()
    elif scrape_student == 'f':
        # Make recommendations to a fake student with predetermined completed courses
        student_completed_courses = course_recommender.get_fake_student_completed_courses()

    # Recommend courses to student
    if execute_recommendation == 'y':
        course_recommender.recommend(student_completed_courses)

    status_reporter.program_execution_time(time.time() - start_time)


if __name__ == "__main__":
    main()

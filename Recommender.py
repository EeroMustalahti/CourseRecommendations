import sys
import time


class Recommender:

    def __init__(self, data_preserver, status_reporter):
        self.preserver = data_preserver
        self.reporter = status_reporter

    def recommend(self, student_completed_courses):
        """Recommends set of courses to student."""
        courses_data = self.preserver.load_courses()
        modules_data = self.preserver.load_modules()
        pass

    def get_fake_student_completed_courses(self):
        """Returns array of courses completed by fake student."""
        return []

    # Checking for file existence
    #import os.path
    #os.path.isfile(fname)

    def recommendd(self, passed_courses, courses_data):
        """TO BE REMOVED"""
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

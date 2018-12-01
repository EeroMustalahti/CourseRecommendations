import sys
import time


class Recommender:

    courses_data = {}
    modules_data = {}
    student_data = {}
    student_faculty = None

    def __init__(self, data_preserver, status_reporter):
        self.preserver = data_preserver
        self.reporter = status_reporter

    def recommend(self, real_student):
        """Recommends set of courses to student."""

        self.load_course_and_module_data()
        if real_student:
            self.load_student_data()

        print(self.student_faculty)
        print(self.student_data)

        pass

    def load_course_and_module_data(self):
        self.courses_data = self.preserver.load_courses()
        self.modules_data = self.preserver.load_modules()

    def load_student_data(self):
        self.student_data = self.preserver.load_student()
        self.student_faculty = self.student_data['faculty']
        del self.student_data['faculty']

    def get_fake_student_completed_courses(self):
        """Returns array of courses completed by fake student."""

        self.student_data = {}
        self.student_faculty = 'LUO'

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

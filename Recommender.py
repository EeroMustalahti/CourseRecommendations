import sys
import time
import copy
import pprint


class Recommender:

    courses_data = {}
    modules_data = {}
    student_data = {}
    student_faculty = None

    fake_students_data = {
        'f1': {
            'faculty': 'Faculty of Natural Sciences',
            'TIETS05': {
                'ects': 5
            },
            'MTTTS20': {
                'ects': 5
            },
        },
        'f2': {
            'faculty': 'Faculty of Natural Sciences',
            'TIEP1': {
                'ects': 5
            },
            'TIEP2': {
                'ects': 5
            },
        },
        'f3': {
            'faculty': 'Faculty of Communication Sciences',
            'ENGS1': {
                'ects': 5
            },
        },
    }

    # For own faculty scores: halfway between given score and 1? (Add them and divide by 2)
    important_module_course = 'important'

    student_modules = {}
    # Might have to be orderable like list / []?
    recommended_courses = {}

    def __init__(self, data_preserver, status_reporter):
        self.preserver = data_preserver
        self.reporter = status_reporter

    def recommend(self, real_student):
        """Recommends set of courses to student."""

        self.load_course_and_module_data()
        if real_student:
            self.load_student_data()

        # Find out all modules where the student has completed some courses
        for key, value in self.student_data.items():
            for study_module in self.courses_data[key]['belongs_to_modules']:
                self.student_modules[study_module] = self.copy_dict(self.modules_data[study_module])

        # For each student's module take courses not completed &
        # mark how much credits have been completed and num of completed courses &
        # count total amount of ECTS if all courses would be completed (for completed course add completed ECTS)
        for module_id, module_info in self.student_modules.items():
            for course_id in module_info['courses']:
                if course_id not in self.student_data:
                    # If not completed course recommendation will be made
                    self.recommended_courses[course_id] = self.copy_dict(self.courses_data[course_id])
                    self.add_credits_to_total_collectable_ects(module_id, self.courses_data[course_id]['ects'])
                else:
                    # If completed add student's ects amount of that course to total completed credits count
                    self.add_student_course_credits(course_id, module_id)
                    self.add_credits_to_total_collectable_ects(module_id, self.student_data[course_id]['ects'])
                    self.increment_number_of_completed_courses(module_id)
            self.student_modules[module_id]['number_of_courses'] = len(self.student_modules[module_id]['courses'])

        pprint.pprint(self.student_modules)
        print('####################')
        pprint.pprint(self.recommended_courses)
        print('*********************')

        # WARNING missing method to calculate score when module has None ECTS

        for module_id, module_info in self.student_modules.items():
            completed_ects = module_info['completed_ects']
            ects = module_info['ects']
            total_collectable_ects = module_info['total_collectable_ects']
            completed_courses = module_info['completed_courses']
            number_of_courses = module_info['number_of_courses']

            if completed_ects >= ects or completed_courses == number_of_courses:
                # If completed credits equal or exceed module's ECTS OR all courses are completed then ignore the module
                continue
            # Choose scoring method. Choose credit if total collectable credit count exceeds module's own ects amount
            if total_collectable_ects > ects:
                # Score for all non-completed courses: completed_ects / module's ects
                score = completed_ects / ects
                for course_id in module_info['courses']:
                    if course_id in self.recommended_courses:
                        self.try_to_assign_score_to_course(course_id, score, module_id, module_info, 'ects')
            else:
                # Score for all non-completed courses: completed_courses / number_of_courses
                score = completed_courses / number_of_courses
                for course_id in module_info['courses']:
                    if course_id in self.recommended_courses:
                        if course_id in self.recommended_courses:
                            self.try_to_assign_score_to_course(course_id, score, module_id, module_info, 'course_amount')

        # Do necessary score raising for courses belonging to student's faculty
        for recommended_id, recommended_info in self.recommended_courses.items():
            if recommended_info['faculty'] == self.student_faculty:
                recommended_info['score'] = (1 + recommended_info['score']) / 2
                recommended_info['reason'] += ' The course belongs to your faculty!'

        pprint.pprint(self.recommended_courses)
        self.preserver.save_recommendations(self.recommended_courses)

    def try_to_assign_score_to_course(self, course_id, score, module_id, module_info, scoring_method):
        # If score not yet given then give it.
        # If score is already given but it is higher then replace.
        if (('score' not in self.recommended_courses[course_id]) or
                ('score' in self.recommended_courses[course_id] and
                         score > self.recommended_courses[course_id]['score'])):
            self.recommended_courses[course_id]['score'] = score
            # Mark the reason why the course is given that point (brings closer to complete some module)
            if scoring_method == 'ects':
                reason = 'Completed {0} ECTS out of {1} ECTS in study module {2} {3}. Only {4} ECTS left!'
                reason = reason.format(module_info['completed_ects'], module_info['ects'], module_id,
                                       module_info['name'], module_info['ects'] - module_info['completed_ects'])
                self.recommended_courses[course_id]['reason'] = reason
            else:
                reason = 'Completed {0} courses out of {1} courses in study module {2} {3}. Only {4} courses left!'
                reason = reason.format(module_info['completed_courses'], module_info['number_of_courses'], module_id,
                                       module_info['name'],
                                       module_info['number_of_courses'] - module_info['completed_courses'])
                self.recommended_courses[course_id]['reason'] = reason

    def add_student_course_credits(self, course_id, module_id):
        if 'completed_ects' in self.student_modules[module_id]:
            self.student_modules[module_id]['completed_ects'] += self.student_data[course_id]['ects']
        else:
            self.student_modules[module_id]['completed_ects'] = self.student_data[course_id]['ects']

    def add_credits_to_total_collectable_ects(self, module_id, addable_credits):
        if 'total_collectable_ects' in self.student_modules[module_id]:
            self.student_modules[module_id]['total_collectable_ects'] += addable_credits
        else:
            self.student_modules[module_id]['total_collectable_ects'] = addable_credits

    def increment_number_of_completed_courses(self, module_id):
        if 'completed_courses' in self.student_modules[module_id]:
            self.student_modules[module_id]['completed_courses'] += 1
        else:
            self.student_modules[module_id]['completed_courses'] = 1

    # Data preserving

    def load_course_and_module_data(self):
        self.courses_data = self.preserver.load_courses()
        self.modules_data = self.preserver.load_modules()

    def load_student_data(self):
        self.student_data = self.preserver.load_student()
        self.student_faculty = self.student_data['faculty']
        del self.student_data['faculty']

    # Fake student generation

    def get_fake_student_completed_courses(self, fake_student_key):
        """Returns array of courses completed by fake student."""

        self.student_data = self.fake_students_data[fake_student_key]
        self.student_faculty = self.student_data['faculty']
        del self.student_data['faculty']

    # Utility methods

    @staticmethod
    def copy_dict(value, key=None):
        value_copy = copy.deepcopy(value)
        if key:
            return {key: value_copy}
        return value_copy

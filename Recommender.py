import copy

from collections import OrderedDict


class Recommender:

    fake_students_data = {
        'f1': {
            'faculty': 'Faculty of Communication Sciences',
            'TIETS05': {
                'ects': 5
            },
            'MTTTS20': {
                'ects': 5
            },
        },
        # Starting LUO Bachelor of Sciences student having completed two basic courses.
        # Should use Completed courses / Number of module's courses + Bonus for own faculty courses
        'f2': {
            'faculty': 'Faculty of Natural Sciences',
            'TIEP1': {
                'ects': 5
            },
            'TIEP2': {
                'ects': 5
            },
        },
        # COMS student completed course in module where no ECTS amount is specified.
        # Should use upper module's ECTS to determine scoring for module's courses because total ects > ancestor's ects
        'f3': {
            'faculty': 'Faculty of Social Sciences',
            'MTTTS20': {
                'ects': 5
            },
            'TIETA17': {
                'ects': 5
            },
        },
        # COMS student completed LUO course in module where total collectable ECTS exceed module's ECTS amount.
        # Should use Completed ECTS / Module's ECTS scoring.
        'f4': {
            'faculty': 'Faculty of Social Sciences',
            'TIEH0': {
                'ects': 10
            },
        },
        # COMS student completed very first course listed in their faculty website.
        # Should use Completed courses / Number of module's courses scoring + Bonus for own faculty.
        'f5': {
            'faculty': 'Faculty of Communication Sciences',
            'ENGS1': {
                'ects': 5
            },
        },
    }

    courses_data = {}  # Dataset of courses
    modules_data = {}  # Dataset of modules
    student_data = {}  # Completed courses by the student
    student_faculty = None  # Faculty where the student belongs to

    student_modules = {}  # Modules where the student has completed at least one course

    recommended_courses = {}  # Courses recommended for the student

    reason_padding = '                        '

    def __init__(self, data_preserver, status_reporter):
        self.preserver = data_preserver
        self.reporter = status_reporter

    def recommend(self, real_student):
        """
        Recommend set of courses to student and saves the recommended courses to file
        :param real_student: Whether we are producing recommendations for real student or not
        """

        self.load_course_and_module_data()
        if real_student:
            # Load real student's study record from file
            self.load_student_data()

        # Gather a set of modules where the student has completed at least one course in each module
        for key, value in self.student_data.items():
            if key in self.courses_data:
                # Ignore student's completed course if it is not in scraped course data
                for study_module in self.courses_data[key]['belongs_to_modules']:
                    if study_module in self.modules_data:
                        # Ignore modules which have not been collected (e.g. Summer School 2018)
                        self.student_modules[study_module] = self.copy_dict(self.modules_data[study_module])

        # Procedure when student module does not have ECTS:
        # Check if parent module has ECTS. If not then check its parent module for ECTS.
        # Recursively until module with ECTS is found.
        # Take the upper module's ECTS. Then for each sub-module in it calculate
        # total_collectable_ects and completed_ects.
        # If total_colletable_ects > upper module's ECTS then recommend module's courses by
        # completed_ects / upper module's ECTS. Else normal course count for the None ECTS module only.

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
                    # If completed add student's ects amount of that course
                    # to total completed credits count in that module
                    self.add_student_course_credits(course_id, module_id)
                    self.add_credits_to_total_collectable_ects(module_id, self.student_data[course_id]['ects'])
                    self.increment_number_of_completed_courses(module_id)

            # Mark the number of courses the module has
            self.student_modules[module_id]['number_of_courses'] = len(self.student_modules[module_id]['courses'])

            # Check if module has no ECTS
            if module_info['ects'] is None:
                ancestor_with_ects = self.find_ancestor_module_with_ects(module_info['parent'])
                if ancestor_with_ects is None:
                    # If no ancestor with ECTS then use course amount complementation
                    module_info['ects'] = 'No ECTS ancestor'
                    continue
                module_info['ancestor_with_ects'] = ancestor_with_ects  # Mark the ancestor with ECTS
                module_info['ects'] = self.modules_data[ancestor_with_ects]['ects']  # Take ancestor's ects as "module's ects"
                # Find all ancestor's sub-modules except this module
                ancestor_and_submodules_except_this = self.find_ancestor_submodules_except_this(
                    ancestor_with_ects, module_id)
                # For each submodule add their completed ECTS and total collectable ECTS to this module's
                for submodule_id in ancestor_and_submodules_except_this:
                    submodule_info = self.modules_data[submodule_id]
                    for course_id in submodule_info['courses']:
                        if course_id not in self.student_data:
                            self.add_credits_to_total_collectable_ects(module_id, self.courses_data[course_id]['ects'])
                        else:
                            self.add_student_course_credits(course_id, module_id)
                            self.add_credits_to_total_collectable_ects(module_id, self.student_data[course_id]['ects'])

        # Calculate scores for courses in student's modules
        for module_id, module_info in self.student_modules.items():

            completed_ects = module_info['completed_ects']
            ects = module_info['ects']
            total_collectable_ects = module_info['total_collectable_ects']
            completed_courses = module_info['completed_courses']
            number_of_courses = module_info['number_of_courses']

            if (isinstance(ects, int) and completed_ects >= ects) or completed_courses == number_of_courses:
                # If completed credits equal or exceed module's ECTS OR all courses are completed then ignore the module
                continue

            # Choose scoring method. Choose credit if total collectable credit count exceeds module's own ects amount
            if isinstance(ects, int) and total_collectable_ects > ects:
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

        # Remove those courses which did not get score assigned to them due to module being already fully completed
        no_unscored = {}
        for recommended_id, recommended_info in self.recommended_courses.items():
            if 'score' in recommended_info:
                no_unscored.update({recommended_id: recommended_info})
        self.recommended_courses = no_unscored

        # Add bonus points for courses belonging to student's faculty
        for recommended_id, recommended_info in self.recommended_courses.items():
            print(recommended_id + ' ' + recommended_info['name'])
            if recommended_info['faculty'] == self.student_faculty:
                recommended_info['score'] = (1 + recommended_info['score']) / 2
                recommended_info['reason'] += ' The course belongs to your faculty!'

        # Make sorted dict from highest score course to lowest score course
        od = OrderedDict(sorted(self.recommended_courses.items(), key=lambda x: x[1]['score'], reverse=True))
        # Save ordered recommended courses
        self.preserver.save_recommendations(od, self.student_data, self.student_faculty)

    # Helper methods

    def find_ancestor_submodules_except_this(self, ancestor_with_ects, module_id):
        some_modules = [ancestor_with_ects]
        submodules_except_this = self.traverse_submodules([], some_modules, module_id)

        return submodules_except_this

    def traverse_submodules(self, found, some_modules, not_include_module):
        for some_module in some_modules:
            if some_module != not_include_module:
                found.append(some_module)
            self.traverse_submodules(found, self.find_childs(some_module), not_include_module)
        return found

    def find_childs(self, module_):
        childs = []
        for key, value in self.modules_data.items():
            if 'parent' in value and value['parent'] == module_:
                childs.append(key)
        return childs

    def find_ancestor_module_with_ects(self, module_id):
        """
        Attempts to find the ID of the ancestor module which has ECTS amount specified
        """
        if module_id is None:
            # If no ancestor module could be found where ECTS is specified
            return None
        if self.modules_data[module_id]['ects'] is not None:
            return module_id
        return self.find_ancestor_module_with_ects(self.modules_data[module_id]['parent'])

    def try_to_assign_score_to_course(self, course_id, score, module_id, module_info, scoring_method):
        """
        Attempts to assign score to course. If he score is already given and the existing score is higher
        than the new value then do not assign new value for the score.
        """
        # If score not yet given then give it.
        # If score is already given but it is higher then replace.
        if (('score' not in self.recommended_courses[course_id]) or
                ('score' in self.recommended_courses[course_id] and
                         score > self.recommended_courses[course_id]['score'])):
            self.recommended_courses[course_id]['score'] = score
            # Mark the reason why the course is given that point (brings closer to complete some module)
            if scoring_method == 'ects':
                reason = ''
                if 'ancestor_with_ects' in module_info:
                    reason = 'Course of module {2} {3}\n' + self.reason_padding +\
                             'Completed {0} ECTS out of {1} ECTS in study module\n' + self.reason_padding + \
                             '{5} {6} and it\'s sub-modules.\n' + self.reason_padding + 'Only {4} ECTS left!'
                    reason = reason.format(module_info['completed_ects'], module_info['ects'], module_id,
                                           module_info['name'], module_info['ects'] - module_info['completed_ects'],
                                           module_info['ancestor_with_ects'],
                                           self.modules_data[module_info['ancestor_with_ects']]['name'])
                else:
                    reason = 'Completed {0} ECTS out of {1} ECTS in study module\n' + self.reason_padding +\
                             '{2} {3}.\n' + self.reason_padding + 'Only {4} ECTS left!'
                    reason = reason.format(module_info['completed_ects'], module_info['ects'], module_id,
                                           module_info['name'], module_info['ects'] - module_info['completed_ects'])
                self.recommended_courses[course_id]['reason'] = reason
            else:
                reason = 'Completed {0} courses out of {1} courses in study module\n' + self.reason_padding +\
                         '{2} {3}.\n' + self.reason_padding + 'Only {4} courses left!'
                reason = reason.format(module_info['completed_courses'], module_info['number_of_courses'], module_id,
                                       module_info['name'],
                                       module_info['number_of_courses'] - module_info['completed_courses'])
                self.recommended_courses[course_id]['reason'] = reason

    def add_student_course_credits(self, course_id, module_id):
        if self.student_data[course_id]['ects'] is None:
            # If student did not get any ECTS from course ignore it
            return
        if 'completed_ects' in self.student_modules[module_id]:
            self.student_modules[module_id]['completed_ects'] += self.student_data[course_id]['ects']
        else:
            self.student_modules[module_id]['completed_ects'] = self.student_data[course_id]['ects']

    def add_credits_to_total_collectable_ects(self, module_id, addable_credits):
        if addable_credits is None:
            # Ignore courses where no credits can be obtained
            return
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
        """
        Loads the courses and modules datasets from files
        """
        self.courses_data = self.preserver.load_courses()
        self.modules_data = self.preserver.load_modules()

    def load_student_data(self):
        """
        Loads student data from file
        """
        self.student_data = self.preserver.load_student()
        self.student_faculty = self.student_data['faculty']
        # Student's faculty has been memorized.
        # It can be deleted from dataset of completed courses.
        del self.student_data['faculty']

    # Fake student generation

    def get_fake_student_completed_courses(self, fake_student_key):
        """
        Prepares the Recommender to make recommendations to artificial student
        :param fake_student_key: The key of the artificial student for who to make recommendations
        """
        self.student_data = self.fake_students_data[fake_student_key]
        self.student_faculty = self.student_data['faculty']
        # Student's faculty has been memorized.
        # It can be deleted from dataset of completed courses.
        del self.student_data['faculty']

    # Utility methods

    @staticmethod
    def copy_dict(value, key=None):
        """
        Copies a dictionary
        :param value:
        :param key: Optional key functioning as the key of the copy dict
        :return: Either only copy of the dict or also a dict having one key with the copied dict as value
        """
        value_copy = copy.deepcopy(value)
        if key:
            return {key: value_copy}
        return value_copy

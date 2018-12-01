import sys
import os
import json


class Preserver:

    courses_file = 'courses_data.json'
    modules_file = 'study_modules_data.json'
    study_record_file = 'NettiOpsu.htm'
    student_file = 'student_data.json'
    recommendations_file = 'recommendations.txt'
    log_file = 'trace_log.txt'

    def __init__(self, status_reporter):
        self.reporter = status_reporter

    def save_courses(self, courses_data):
        self.save(self.courses_file, courses_data)
        self.reporter.courses_saved(self.courses_file)

    def save_modules(self, modules_data):
        self.save(self.modules_file, modules_data)
        self.reporter.modules_saved(self.modules_file)

    def save_student_data(self, student_data):
        self.save(self.student_file, student_data)
        self.reporter.student_saved(self.student_file)

    def save_recommendations(self, recommendations_data):
        with open(self.recommendations_file, 'w') as f:
            for key, value in recommendations_data.items():
                id_     = '                        ID : {0}'.format(key)
                name    = '                      Name : {0}'.format(value['name'])
                ects    = '                      ECTS : {0}'.format(value['ects'])
                modules = '        Belongs to modules :'
                for module_ in value['belongs_to_modules']:
                    modules += ' {0}'.format(module_)
                faculty = '                   Faculty : {0}'.format(value['faculty'])
                score   = '      Recommendation score : {0}'.format(value['score'])
                reason  = 'Reason to take this course : {0}'.format(value['reason'])
                f.write(id_ + '\n')
                f.write(name + '\n')
                f.write(ects + '\n')
                f.write(modules + '\n')
                f.write(faculty + '\n')
                f.write(score + '\n')
                f.write(reason + '\n\n')

        self.reporter.recommendations_saved(self.recommendations_file)

    def load_study_record(self):
        with open(self.study_record_file) as f:
            s = f.read()
            f.close()
            return s

    def load_courses(self):
        try:
            courses_data = self.load(self.courses_file)
            self.reporter.courses_loaded(self.courses_file)
            return courses_data
        except IOError:
            sys.exit(self.reporter.no_courses_file(self.courses_file))

    def load_modules(self):
        try:
            modules_data = self.load(self.modules_file)
            self.reporter.modules_loaded(self.modules_file)
            return modules_data
        except IOError:
            sys.exit(self.reporter.no_modules_file(self.modules_file))

    def load_student(self):
        try:
            student_data = self.load(self.student_file)
            self.reporter.student_loaded(self.student_file)
            return student_data
        except IOError:
            sys.exit(self.reporter.no_student_file(self.student_file))

    def delete_logfile(self):
        try:
            os.remove(self.log_file)
        except OSError:
            pass

    def append_to_log_file(self, log_entry):
        self.append(self.log_file, log_entry)

    @staticmethod
    def append(file, entry):
        with open(file, 'a') as f:
            f.write(entry + '\n')
            f.close()

    @staticmethod
    def save(file, data):
        with open(file, 'w') as f:
            json.dump(data, f)

    @staticmethod
    def load(file):
        with open(file) as f:
            return json.load(f)

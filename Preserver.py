import sys
import json

from Reporter import Reporter


class Preserver:

    courses_file = 'courses.json'
    modules_file = 'study_modules.json'
    recommendations_file = 'recommendations.json'
    reporter = Reporter()

    def __init__(self):
        pass

    def save_courses(self, courses_data):
        self.save(self.courses_file, courses_data)
        self.reporter.courses_saved(self.courses_file)

    def save_modules(self, modules_data):
        self.save(self.modules_file, modules_data)
        self.reporter.modules_saved(self.modules_file)

    def save_recommendations(self, recommendations):
        pass

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
            sys.exit(self.reporter.no_modules_file(self.courses_file))

    @staticmethod
    def save(file, data):
        with open(file, 'w') as f:
            json.dump(data, f)

    @staticmethod
    def load(file):
        with open(file) as f:
            return json.load(f)

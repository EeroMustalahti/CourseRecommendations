import json

from Reporter import Reporter


class Preserver:

    courses_file = 'courses.json'
    modules_file = 'study_modules.json'
    reporter = Reporter()

    def __init__(self):
        pass

    def save_courses(self, courses_data):
        self.save(self.courses_file, courses_data)
        self.reporter.courses_saved(self.courses_file)

    def save_modules(self, modules_data):
        self.save(self.modules_file, modules_data)
        self.reporter.modules_saved(self.modules_file)

    def load_courses(self):
        courses_data = self.load(self.courses_file)
        self.reporter.courses_loaded(self.courses_file)
        return courses_data

    def load_modules(self):
        modules_data = self.load(self.modules_file)
        self.reporter.modules_loaded(self.modules_file)
        return modules_data

    @staticmethod
    def save(file, data):
        with open(file, 'w') as f:
            json.dump(data, f)

    @staticmethod
    def load(file):
        with open(file) as f:
            return json.load(f)

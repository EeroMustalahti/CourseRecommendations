import datetime


class Reporter:

    passed_time = 'Passed time since start of scraping: '
    enter_faculty = 'ENTERING FACULTY: '
    enter_programme = 'ENTERING PROGRAMME: '
    module_collected = 'MODULE: %s | %s | %s ECTS | %s'
    module_courses = 'Courses:'
    course_collected = 'COURSE: %s | %s | %s ECTS'
    course_already_collected = 'Course %s %s has already been collected'
    cannot_collect_course = 'Cannot collect course data. The course page seems to not work correctly.'
    course_modules = 'Belongs to modules:'

    uta_scrape_time = 'Time to collect courses and study modules data: '

    saved_courses = 'Courses data has been saved to file: '
    saved_modules = 'Study modules data has been saved to file: '
    loaded_courses = 'Courses data has been loaded from file: '
    loaded_modules = 'Study modules data has been loaded from file: '

    execute_scrape = 'Execute scraping process which creates the file before executing recommendation process.'
    no_courses = 'File %s containing courses data seems to not exist.\n' + execute_scrape
    no_modules = 'File %s containing study modules data seems to not exist.\n' + execute_scrape

    execution_time = 'Time to execute the program: %s'

    full_logging = 'full'
    intermediate_logging = 'intermediate'
    minimum_logging = 'minimum'

    def __init__(self, logging_amount, logging_amount_to_file, data_preserver=None):

        logging_amount = self.full_logging if logging_amount == 'f' else\
            self.intermediate_logging if logging_amount == 'i' else self.minimum_logging
        logging_amount_to_file = self.full_logging if logging_amount_to_file == 'f' else\
            self.intermediate_logging if logging_amount_to_file == 'i' else self.minimum_logging

        self.logging_amount = logging_amount
        self.logging_amount_to_file = logging_amount_to_file

        self.preserver = data_preserver

    def delete_old_logfile(self):
        self.preserver.delete_logfile()

    def entering_faculty(self, faculty):
        self.log(self.enter_faculty + faculty, self.minimum_logging)

    def entering_programme(self, programme):
        self.log(self.enter_programme + programme, self.minimum_logging)

    def module_data_collected(self, module_data, module_id):
        self.log(self.module_collected % (module_id, module_data[module_id]['name'],
                                          str(module_data[module_id]['ects']),
                                          module_data[module_id]['parent']), self.intermediate_logging)
        self.log(self.module_courses, self.full_logging)
        for course_id in module_data[module_id]['courses']:
            self.log('  ' + course_id, self.full_logging)

    def course_data_collected(self, course_data, course_id):
        self.log(self.course_collected % (course_id, course_data[course_id]['name'],
                                          str(course_data[course_id]['ects'])), self.intermediate_logging)
        self.log(self.course_modules, self.full_logging)
        for module_id in course_data[course_id]['belongs_to_modules']:
            self.log('  ' + module_id, self.full_logging)

    def course_data_already_collected(self, course_data, course_id):
        self.log(self.course_already_collected % (course_id, course_data[course_id]['name']), self.intermediate_logging)

    def cannot_collect_course_data(self):
        self.log(self.cannot_collect_course, self.intermediate_logging)

    def scrape_time_passed(self, passed_time):
        self.log(self.passed_time + self.display_hours_and_minutes(passed_time), self.minimum_logging)

    def uta_scrape_time_span(self, time_span):
        self.log(self.uta_scrape_time + self.display_hours_and_minutes(time_span), self.minimum_logging)

    def courses_saved(self, file_name):
        self.log(self.saved_courses + file_name, self.minimum_logging)

    def modules_saved(self, file_name):
        self.log(self.loaded_courses + file_name, self.minimum_logging)

    def courses_loaded(self, file_name):
        self.log(self.loaded_courses + file_name, self.minimum_logging)

    def modules_loaded(self, file_name):
        self.log(self.loaded_modules + file_name, self.minimum_logging)

    def no_courses_file(self, file_name):
        self.log(self.no_courses % file_name, self.minimum_logging)

    def no_modules_file(self, file_name):
        self.log(self.no_modules + file_name, self.minimum_logging)

    def program_execution_time(self, time):
        self.log(self.execution_time % self.display_hours_and_minutes(time), self.minimum_logging)

    # Utility methods

    def log(self, log_entry, log_level):
        if self.entry_must_be_logged(self.logging_amount, log_level):
            print(log_entry)
        if self.entry_must_be_logged(self.logging_amount_to_file, log_level):
            self.preserver.append_to_log_file(log_entry)

    def entry_must_be_logged(self, used_log_level, entry_log_level):
        if used_log_level == self.intermediate_logging and entry_log_level == self.full_logging:
            return False
        if used_log_level == self.minimum_logging and\
                (entry_log_level == self.full_logging or entry_log_level == self.intermediate_logging):
            return False
        return True

    @staticmethod
    def display_hours_and_minutes(seconds):
        return str(datetime.timedelta(seconds=seconds))

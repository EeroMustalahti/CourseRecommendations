import datetime


class Reporter:

    passed_time = 'Passed time since start of scraping: '
    enter_faculty = 'Scraping process entering faculty: '
    enter_programme = 'Scraping process entering study programme: '
    course_collected = 'Collected data of course: '
    module_collected = 'Collected data of study module: '

    uta_scrape_time = 'Time to collect course and study module data: '

    saved_courses = 'Courses data has been saved to file: '
    saved_modules = 'Study modules data has been saved to file: '
    loaded_courses = 'Courses data has been loaded from file: '
    loaded_modules = 'Study modules data has been loaded from file: '

    def __init__(self):
        pass

    def entering_faculty(self, faculty):
        print(self.enter_faculty + faculty)

    def entering_programme(self, programme):
        print(self.enter_programme + programme)

    def course_data_collected(self, course_id, course_name):
        print(self.course_collected + course_id + ' ' + course_name)

    def module_data_collected(self, module_name):
        print(self.module_collected + module_name)

    def scrape_time_passed(self, passed_time):
        print(self.passed_time + self.display_hours_and_minutes(passed_time))

    def uta_scrape_time_span(self, time_span):
        print(self.uta_scrape_time + self.display_hours_and_minutes(time_span))

    def courses_saved(self, file_name):
        print(self.saved_courses + file_name)

    def modules_saved(self, file_name):
        print(self.loaded_courses + file_name)

    def courses_loaded(self, file_name):
        print(self.loaded_courses + file_name)

    def modules_loaded(self, file_name):
        print(self.loaded_modules + file_name)

    @staticmethod
    def display_hours_and_minutes(seconds):
        return str(datetime.timedelta(seconds=seconds))
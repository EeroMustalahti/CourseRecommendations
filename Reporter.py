import datetime


class Reporter:

    passed_time = 'Passed time since start of scraping: '
    enter_faculty = 'ENTERING FACULTY: '
    enter_programme = 'ENTERING PROGRAMME: '
    module_collected = 'MODULE: %s | %s | %s ECTS | %s'
    module_courses = 'Courses:'
    course_collected = 'COURSE: %s | %s | %s ECTS'
    course_modules = 'Belongs to modules:'

    uta_scrape_time = 'Time to collect courses and study modules data: '

    saved_courses = 'Courses data has been saved to file: '
    saved_modules = 'Study modules data has been saved to file: '
    loaded_courses = 'Courses data has been loaded from file: '
    loaded_modules = 'Study modules data has been loaded from file: '

    execute_scrape = 'Execute scraping process which creates the file before executing recommendation process.'
    no_courses = 'File %s containing courses data seems to not exist.\n' + execute_scrape
    no_modules = 'File %s containing study modules data seems to not exist.\n' + execute_scrape

    def __init__(self):
        pass

    def entering_faculty(self, faculty):
        print(self.enter_faculty + faculty)

    def entering_programme(self, programme):
        print(self.enter_programme + programme)

    def module_data_collected(self, module_data, module_id):
        print(self.module_collected % (module_id, module_data[module_id]['name'],
                                       str(module_data[module_id]['ects']), module_data[module_id]['parent']))
        print(self.module_courses)
        for course_id in module_data[module_id]['courses']:
            print('  ' + course_id)

    def course_data_collected(self, course_data, course_id):
        print(self.course_collected % (course_id, course_data[course_id]['name'], str(course_data[course_id]['ects'])))
        print(self.course_modules)
        for module_id in course_data[course_id]['belongs_to_modules']:
            print('  ' + module_id)

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

    def no_courses_file(self, file_name):
        print(self.no_courses % file_name)

    def no_modules_file(self, file_name):
        print(self.no_modules + file_name)

    @staticmethod
    def display_hours_and_minutes(seconds):
        return str(datetime.timedelta(seconds=seconds))

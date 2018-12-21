

class CommandReader:

    needed_cmd_line_args = 7

    # Default values for the commands
    scrape_data = False
    student_data = 'f5'
    student_faculty = 'Faculty of Natural Sciences'
    execute_recommendation = False
    logging_amount = 'i'
    logging_amount_to_file = 'f'

    # Instruction texts for the user to explain available commands
    scrape_data_text = "Scrape university website to collect the courses dataset? " \
                       "(y = yes, other = no): "
    student_data_text = "Collect university student's study record? " \
                        "(y = yes, " \
                        "f1 = no, use fake student 1, " \
                        "f2 = no, use fake student 2, " \
                        "f3 = no, use fake student 3, " \
                        "f4 = no, use fake student 4, " \
                        "other = no, use fake student 5): "
    student_faculty_text = "What is the student's faculty? " \
                           "(coms = Faculty of Communication Sciences, " \
                           "edu = Faculty of Education, " \
                           "jkk = Faculty of Management, " \
                           "med = Faculty of Medicine and Life Sciences, " \
                           "soc = Faculty of Social Sciences, " \
                           "other = Faculty of Natural Sciences): "
    execute_recommendation_text = "Make recommendations to a student? " \
                                  "(y = yes, other = no): "

    logging_amount_text = "How much logging is done to standard output to trace the execution of the program? " \
                          "(f = full ," \
                          "m = minimum: all except when individual module or course data is collected, " \
                          "other = intermediate: all except module's courses and modules where course belong): "
    logging_amount_to_file_text = "How much logging is saved to a file to trace the execution of the program? " \
                                  "(i = intermediate: all except module's courses and modules where course belong ," \
                                  "m = minimum: all except when individual module or course data is collected, " \
                                  "other = full): "

    error_text = 'Use only specified commands!'

    def get_user_input(self, argv):
        """
        Read the commands that the user issues to the program
        :param argv: Command line arguments
        :return: Commands guiding the execution of the program
        """
        if len(argv) == self.needed_cmd_line_args:
            self.get_input_from_command_line(argv)
        else:
            self.get_input_from_keyboard()
        return self.scrape_data, self.student_data, self.student_faculty, self.execute_recommendation,\
               self.logging_amount, self.logging_amount_to_file

    def get_input_from_command_line(self, argv):
        """
        Read commands from command line arguments
        :param argv: Command line arguments
        """
        self.scrape_data_input_convert(argv[1])
        self.student_data_input_convert(argv[2])
        self.student_faculty_input_convert(argv[3])
        self.execute_recommendation_input_convert(argv[4])

        self.logging_amount_input_convert(argv[5])
        self.logging_amount_to_file_input_convert(argv[6])

    def get_input_from_keyboard(self):
        """
        Ask commands from the user directly and read them from standard input
        """
        print('Course recommender system (Eero Mustalahti & Daniel Sell)')
        scrape_data = input(self.scrape_data_text) or None
        self.scrape_data_input_convert(scrape_data)

        student_data = input(self.student_data_text) or None
        self.student_data_input_convert(student_data)

        if self.student_data == 'y':
            # Ask faculty only if recommendations are made to real student
            student_faculty = input(self.student_faculty_text) or None
            self.student_faculty_input_convert(student_faculty)

        execute_recommendation = input(self.execute_recommendation_text) or None
        self.execute_recommendation_input_convert(execute_recommendation)

        logging_amount = input(self.logging_amount_text) or None
        self.logging_amount_input_convert(logging_amount)

        logging_amount_to_file = input(self.logging_amount_to_file_text) or None
        self.logging_amount_to_file_input_convert(logging_amount_to_file)

    def scrape_data_input_convert(self, value):
        """
        Converts the user's command on whether to scrape dataset or not to correct form
        :param value: The value to convert
        """
        if value == 'y':
            self.scrape_data = True
            print('=> Yes')
        else:
            print('=> No')

    def student_data_input_convert(self, value):
        """
        Converts the user's command on whether to make recommendations for real student or
        some artificial student with artificial study record to correct form
        :param value: The value to convert
        """
        if value == 'y':
            self.student_data = 'y'
            print('=> Yes')
        elif value == 'f1':
            self.student_data = 'f1'
            print('=> Fake student 1')
        elif value == 'f2':
            self.student_data = 'f2'
            print('=> Fake student 2')
        elif value == 'f3':
            self.student_data = 'f3'
            print('=> Fake student 3')
        elif value == 'f4':
            self.student_data = 'f4'
            print('=> Fake student 4')
        else:
            print('=> Fake student 5')

    def student_faculty_input_convert(self, value):
        """
        Converts the user's command on what is the real student's faculty to correct form
        :param value: The value to convert
        """
        if value == 'coms':
            self.student_faculty = 'Faculty of Communication Sciences'
            print('=> Faculty of Communication Sciences')
        elif value == 'edu':
            self.student_faculty = 'Faculty of Education'
            print('=> Faculty of Education')
        elif value == 'jkk':
            self.student_faculty = 'Faculty of Management'
            print('=> Faculty of Management')
        elif value == 'med':
            self.student_faculty = 'Faculty of Medicine and Life Sciences'
            print('=> Faculty of Medicine and Life Sciences')
        elif value == 'soc':
            self.student_faculty = 'Faculty of Social Sciences'
            print('=> Faculty of Social Sciences')
        else:
            print('=> Faculty of Natural Sciences')

    def execute_recommendation_input_convert(self, value):
        """
        Converts the user's command on whether to make recommendations to correct form
        :param value: The value to convert
        """
        if value == 'y':
            self.execute_recommendation = True
            print('=> Yes')
        else:
            print('=> No')

    def logging_amount_input_convert(self, value):
        """
        Converts the user's command on how much logging is printed to the standard output stream to correct form
        :param value: The value to convert
        """
        if value == 'f':
            self.logging_amount = 'f'
            print('=> Full')
        elif value == 'm':
            self.logging_amount = 'm'
            print('=> Minimum')
        else:
            print('=> Intermediate')

    def logging_amount_to_file_input_convert(self, value):
        """
        Converts the user's command on how much logging is written to a log file generated by the program
        to correct form
        :param value: The value to convert
        """
        if value == 'i':
            self.logging_amount_to_file = 'i'
            print('=> Intermediate')
        elif value == 'm':
            self.logging_amount_to_file = 'm'
            print('=> Minimum')
        else:
            print('=> Full')

def gen_student_actual_choices(config, model = None):

    d_instance = {
        d_student['student_id']: {
            d_school_zoned['nces_id']: d_student['actual_school']
            for d_school_zoned in config.l_schools
        }
        for d_student in config.l_students
    }
    return d_instance
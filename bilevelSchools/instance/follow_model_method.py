def gen_student_actual_choices(config, model = None):

    d_instance = {
        d_student['student_id']: {
            d_school_zoned['nces_id']: get_1_choice(config, d_student, d_school_zoned)
            for d_school_zoned in config.l_schools
        }
        for d_student in config.l_students
    }
    return d_instance

def get_1_choice(config, d_student, d_school_zoned):

    ### this is the assumption we used in the paper
    if d_student['zoned_school'] == d_school_zoned['nces_id']:
        return d_student['actual_school']
    else:
        return d_school_zoned['nces_id']
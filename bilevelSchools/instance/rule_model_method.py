import numpy as np

from bilevelSchools.classification.ruleBased import gen_1_distribution
from bilevelSchools.utils import data_utils as du

# well this is just a test method
def gen_student_actual_choices(config, model):

    d_time = du.loadJson(config.s_travel_time_json_path)
    d_instance = {
        d_student['student_id']: {
            d_school_zoned['nces_id']: get_1_choice(config, d_time, d_student, d_school_zoned)
            for d_school_zoned in config.l_schools
        }
        for d_student in config.l_students
    }
    return d_instance


def get_1_choice(config, d_time, d_student, d_school_zoned):

    ### this is the assumption we used in the paper
    if d_student['zoned_school'] == d_school_zoned['nces_id']:
        return d_student['actual_school']

    return np.random.choice(
        config.l_school_ids,
        1,
        p = gen_1_distribution(config, d_time, d_student, d_school_zoned['nces_id'])
    )[0]
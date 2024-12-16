import math, random

from bilevelSchools.utils import data_utils as du

def report(config):

    ### Initailize
    d_students = {
        d_student['student_id']: d_student
        for d_student in config.l_students
    }

    d_student_opt_out_count = {
        d_student['student_id']: 0
        for d_student in config.l_students
    }

    ### CB results
    d_cb_results = du.loadJson(
        config.s_result_cb_json_path
    )

    random.seed(config.i_random_seed_for_picking_instances)
    l_selected_instances_idx = random.sample(
        range(1, config.i_num_possible_instances + 1),
        config.i_num_instances
    )

    ### Find who opt out
    for i_instance_idx in l_selected_instances_idx:

        d_student_choices = du.loadJson(
            config.s_1_choice_instance_json_path.format(i_instance_idx)
        )

        for s_student_id in d_student_choices:

            s_cb_id = d_students[s_student_id]['census_block']

            s_school_id_zoned = d_cb_results[s_cb_id]['new_zoned_school']
            s_school_id_goto  = d_student_choices[s_student_id][s_school_id_zoned]

            if s_school_id_goto != s_school_id_zoned:
                d_student_opt_out_count[s_student_id] += 1


    ### Rerport statistics
    i_num_student_optout         = 0
    i_num_student_optout_white   = 0
    i_num_student_optout_low_ses = 0

    for s_student_id in d_student_choices:

        if d_student_opt_out_count[s_student_id] >= (
            math.floor(config.i_num_instances)
        ):

            i_num_student_optout += 1

            if d_students[s_student_id]['race'] == 'white':
                i_num_student_optout_white += 1

            if config.d_cbs[
                d_students[s_student_id]['census_block']
            ]['ses_level'] == 0:
                i_num_student_optout_low_ses += 1


    print('{} student opt-out more than half instances'.format(i_num_student_optout))
    print('{} {}% white students'.format(
        i_num_student_optout_white,
        round(i_num_student_optout_white / i_num_student_optout * 100, 2)
    ))
    print('{} {}% low ses students'.format(
        i_num_student_optout_low_ses,
        round(i_num_student_optout_low_ses / i_num_student_optout * 100, 2)
    ))
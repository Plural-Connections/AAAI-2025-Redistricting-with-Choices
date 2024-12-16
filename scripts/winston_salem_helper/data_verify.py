import sys
sys.path.append('../../')

from bilevelSchools.configuration import configuration

# --s_input_dir_par_yaml_path place_holder.yaml
if __name__ == '__main__':

    config = configuration.Config()
    config._load_key_data()

    i_pop_sum_from_cb_data = sum(
        config.d_cbs[s_cb_id]['total_students_in_cb']
        for s_cb_id in config.l_cb_ids
    )

    i_pop_sum_from_school_data = sum(
        config.d_schools[s_school_id]['total_student_in_school']
        for s_school_id in config.l_school_ids
    )
    print(i_pop_sum_from_cb_data, i_pop_sum_from_school_data)

    d_school_pops_current = {
        s_school_id: {'low_ses': 0, 'total': 0}
        for s_school_id in config.l_school_ids
    }
    d_cb_pops = {
        s_cb_id: {'low_ses': 0, 'total': 0}
        for s_cb_id in config.l_cb_ids
    }
    for d_student in config.l_students:

        ### basic info
        s_student_id    = d_student['student_id']
        s_cb_id_student = d_student['census_block']
        s_school_id_actual = d_student['actual_school']

        # we will study the dissimilarity of low ses_level and other ses_level
        if config.d_cbs[s_cb_id_student]['ses_level'] == 0:
            d_cb_pops[s_cb_id_student]['low_ses'] += 1
            d_school_pops_current[s_school_id_actual]['low_ses'] += 1


        # attach total population
        d_cb_pops[s_cb_id_student]['total'] += 1
        d_school_pops_current[s_school_id_actual]['total'] += 1


    print(d_school_pops_current)
import sys
sys.path.append('../../')

from bilevelSchools.configuration import configuration
from bilevelSchools.utils import data_utils as du

# --s_input_dir_par_yaml_path place_holder.yaml
if __name__ == '__main__':

    config = configuration.Config()
    config._load_school_data()

    d_school_apperance = {
        s_school_id: 0
        for s_school_id in config.l_school_ids
    }
    for i_instance_idx in range(1, config.i_num_instances + 1):
        print(config.s_1_choice_instance_json_path.format(i_instance_idx))
        d_student_choices = du.loadJson(
            config.s_1_choice_instance_json_path.format(i_instance_idx)
        )

        for s_student_id in d_student_choices:
            for s_school_id_zoned in config.l_school_ids:
                s_school_id_goto = d_student_choices[s_student_id][s_school_id_zoned]
                d_school_apperance[s_school_id_goto] += 1


    for s_school_id in config.l_school_ids:
        print(s_school_id, d_school_apperance[s_school_id])
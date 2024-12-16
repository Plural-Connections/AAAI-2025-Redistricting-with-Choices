import sys

from bilevelSchools.utils import data_utils as du
from bilevelSchools.instance import follow_model_method, ml_model_method, rule_model_method, get_current_choices

def run_generate_instance_pipeline(config, i_instance_idx = None):

    if i_instance_idx == None:
        l_instances_idx = list(range(1, config.i_num_possible_instances + 1))
    else:
        l_instances_idx = [i_instance_idx]

    print('Using {} method'.format(config.s_gen_instance_method))

    if config.s_gen_instance_method == 'current':
        model = None
        gen_student_actual_choices = get_current_choices.gen_student_actual_choices
    elif config.s_gen_instance_method == 'follow':
        model = None
        gen_student_actual_choices = follow_model_method.gen_student_actual_choices
    elif config.s_gen_instance_method == 'rule_based':
        model = None
        gen_student_actual_choices = rule_model_method.gen_student_actual_choices
    elif config.s_gen_instance_method == 'ml_model':
        ### at here we are just using xgboost because it outperforms logit
        config.load_feature_collection()
        model = ml_model_method.train_or_load_a_model_with_full_set(config)
        if config.b_train_a_new_model_to_generate_instance:
            sys.exit()
        gen_student_actual_choices = ml_model_method.gen_student_actual_choices
    else:
        raise ValueError('There is no such method to generate instances')

    for i_idx in l_instances_idx:
        d_instance = gen_student_actual_choices(config, model)
        du.saveJson(
            d_instance,
            config.s_1_choice_instance_json_path.format(i_idx)
        )
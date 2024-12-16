import random

if __name__ == '__main__':

    with open("pars_rezone_stable_test.txt", "w") as file:

        for s_method in ['ml', 'rb']:

            for i in range(1, 101):
                i_random_seed = random.sample(range(1, 100000), 1)[0]


                if s_method == 'ml':
                    s_yaml_file_name = './experiments/aaai2025/pars_ml_with_choices_xgboost.yaml'
                    s_optimization_result_dir = 'scratch/bilevel_school_ml_stable_test/optimization_ml_with_choices' + '_' + str(i_random_seed)
                else:
                    s_yaml_file_name = './experiments/aaai2025/pars_rb_with_choices.yaml'
                    s_optimization_result_dir = 'scratch/bilevel_school_rb_stable_test/optimization_rb_with_choices' + '_' + str(i_random_seed)

                l_line = [
                    '--s_input_dir_par_yaml_path',
                    s_yaml_file_name,

                    '--s_optimization_result_dir',
                    s_optimization_result_dir,

                    '--i_random_seed_for_picking_instances',
                    str(i_random_seed),

                    '--i_cp_max_solving_hour',
                    '10'

                ]

                file.write(' '.join(l_line) + '\n')



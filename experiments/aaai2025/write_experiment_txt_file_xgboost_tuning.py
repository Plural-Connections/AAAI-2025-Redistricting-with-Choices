import random

if __name__ == '__main__':

    with open("pars_xgboost_tuning.txt", "w") as file:

        # can change 1 to other integers, to repeat this process multiple times
        for _ in range(1):
            [i_random_seed_1, i_random_seed_2] = random.sample(range(1, 100000), 2)

            for f_xgboost_eta in [0.08, 0.1, 0.12]:
                for i_xgboost_max_depth in [4, 6, 8, 10, 12]:

                    l_line = [
                        '--s_input_dir_par_yaml_path',
                        "./experiments/aaai2025/pars_ml_with_choices_xgboost.yaml",

                        '--s_classification_result_dir',
                        "scratch/tuning_seeds_{}_{}/xgboost_tuning_{}_{}".format(
                            i_random_seed_1, i_random_seed_2,
                            f_xgboost_eta,   i_xgboost_max_depth
                        ),

                        '--f_xgboost_eta',
                        str(f_xgboost_eta),

                        '--i_xgboost_max_depth',
                        str(i_xgboost_max_depth),

                        '--i_random_seed_for_cross_valid',
                        str(i_random_seed_1),

                        '--i_random_seed_for_train_valid_split',
                        str(i_random_seed_2)

                    ]

                    file.write(' '.join(l_line) + '\n')



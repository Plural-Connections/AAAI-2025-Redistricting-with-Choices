import json, os

if __name__ == '__main__':

    # change these two everytime review the results
    i_seed_1 = 42294
    i_seed_2 = 69812
    f_avg_acc_best = 0
    for f_xgboost_eta in [0.08, 0.1, 0.12]:
        for i_xgboost_max_depth in [4, 6, 8, 10, 12]:

            s_json_partial_path = "scratch/tuning_seeds_{}_{}/xgboost_tuning_{}_{}/validate_set_accuracy.json".format(
                i_seed_1, i_seed_2,
                f_xgboost_eta, i_xgboost_max_depth
            )
            s_json_path = os.path.join(
                os.environ.get('HOME'),
                s_json_partial_path
            )

            with open(s_json_path, 'r') as json_file:
                d_1_res = json.load(json_file)
                f_avg_acc = d_1_res['validate_acc_avg']

            print(
                'Eta {}, max_depth {}, avg acc on validation set {}:'.format(
                    f_xgboost_eta, i_xgboost_max_depth, f_avg_acc
                )
            )

            if f_avg_acc > f_avg_acc_best:
                f_avg_acc_best = f_avg_acc
                print('---------- Best Parameters so far: {} {}, should use the test set result from this one'.format(f_xgboost_eta, i_xgboost_max_depth))
            else:
                pass

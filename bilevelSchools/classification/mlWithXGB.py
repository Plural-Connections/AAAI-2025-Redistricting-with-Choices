import copy, statistics
from sklearn.model_selection import StratifiedKFold, train_test_split
from scipy.special import softmax
import pandas as pd, numpy as np, xgboost as xgb

from bilevelSchools.utils import data_utils as du
from bilevelSchools.classification import reporter, featureProcessers

def classify(config):

    ### Load everything from previous step
    l_features = du.loadJson(
        config.s_ml_features_json_path
    )
    df_features = pd.DataFrame(l_features)
    print('{} features are here'.format(len(df_features.columns)))

    ### Labels
    l_y_all = du.loadJson(
        config.s_ml_labels_json_path
    )


    ### Split by Fold
    fold_splitter = StratifiedKFold(
        n_splits = config.i_num_folds,
        shuffle = True,
        random_state = config.i_random_seed_for_cross_valid
    )
    l_y_gt_overall        = []
    l_y_predict_overall   = []
    l_validate_acc_folds  = []
    l_fold_test_basic_res = []
    i_fold_idx = 1
    for l_train_validate_idx, l_test_idx in fold_splitter.split(df_features, l_y_all):


        ### Get Train / Validate Info
        df_X_train_validate = df_features.iloc[l_train_validate_idx]
        l_y_train_validate  = du.rebuild_list_with_idx(l_y_all, l_train_validate_idx)

        ### Get Test Features / Labels
        df_X_test = df_features.iloc[l_test_idx]
        l_y_test  = du.rebuild_list_with_idx(l_y_all, l_test_idx)


        ### Transform Categorical Featureres
        df_X_train_validate, df_X_test = featureProcessers.label_encode_categorical_features(
            config,
            df_X_train_validate,
            df_X_test
        )

        ### Transform Continuous and Discrete Features, not really necessary but hey
        df_X_train_validate, df_X_test = featureProcessers.normalize_numerical_features(
            config,
            df_X_train_validate,
            df_X_test
        )

        ### split validate and train, temp
        df_X_train, df_X_validate, l_y_train, l_y_validate = train_test_split(
            df_X_train_validate, l_y_train_validate,
            shuffle      = True,
            stratify     = l_y_train_validate,
            train_size   = config.f_training_ratio_in_train_validate,
            random_state = config.i_random_seed_for_train_valid_split
        )


        ### Config parameters for xgboost
        d_train_params = copy.deepcopy(config.d_xgboost_basic_params)
        d_train_params['num_class'] = len(set(l_y_all))
        d_train_params['max_depth'] = config.i_xgboost_max_depth
        d_train_params['eta']       = config.f_xgboost_eta
        print(d_train_params)

        dm_train    = xgb.DMatrix(df_X_train,    label = np.array(l_y_train),    enable_categorical = True)
        dm_validate = xgb.DMatrix(df_X_validate, label = np.array(l_y_validate), enable_categorical = True)


        ### Train the XGBoost model
        model = xgb.train(
            d_train_params, dm_train, config.i_num_rounds,
            evals = [(dm_train, 'train'), (dm_validate, 'valid')],
            early_stopping_rounds = config.i_early_stopping_round,
            verbose_eval = True
        )


        ### Start to evaluate train result
        a_margin_raw_train  = model.predict(xgb.DMatrix(df_X_train, enable_categorical = True), output_margin = True)
        a_y_train_pred_dist = softmax(a_margin_raw_train, axis = 1)
        l_y_train_pred      = np.argmax(a_y_train_pred_dist, axis = 1)
        _ = reporter.evaluate_with_common_metrics(
            config, l_y_train, l_y_train_pred, a_y_train_pred_dist, s_task_type = 'training'
        )

        ### Record Validation Result
        a_margin_raw_validate  = model.predict(xgb.DMatrix(df_X_validate, enable_categorical = True), output_margin = True)
        a_y_validate_pred_dist = softmax(a_margin_raw_validate, axis = 1)
        l_y_validate_pred      = np.argmax(a_y_validate_pred_dist, axis = 1)
        d_fold_basic_validate_res = reporter.evaluate_with_common_metrics(
            config, l_y_validate, l_y_validate_pred, a_y_validate_pred_dist, s_task_type = 'validate'
        )
        l_validate_acc_folds.append(d_fold_basic_validate_res['acc'])

        ### Start to evaluate test result
        a_margin_raw_test  = model.predict(xgb.DMatrix(df_X_test, enable_categorical = True), output_margin = True)
        a_y_test_pred_dist = softmax(a_margin_raw_test, axis = 1)
        l_y_test_pred      = np.argmax(a_y_test_pred_dist, axis = 1)
        d_fold_basic_test_res = reporter.evaluate_with_common_metrics(
            config, l_y_test, l_y_test_pred, a_y_test_pred_dist, s_task_type = 'test'
        )
        l_fold_test_basic_res.append(d_fold_basic_test_res)

        ### save 2 things for potential analyze
        np.save(
            config.s_test_set_distribution_npy_path.format(i_fold_idx),
            a_y_test_pred_dist
        )
        du.saveJson(
            l_y_test,
            config.s_test_set_labels_json_path.format(i_fold_idx)
        )


        ### append
        l_y_gt_overall += l_y_test
        l_y_predict_overall += l_y_test_pred.tolist()

        i_fold_idx += 1


    ### save for hyper-parameter tuning on validate set
    du.saveJson(
        {
            'validate_acc_avg': statistics.mean(l_validate_acc_folds),
            'validate_acc_folds': l_validate_acc_folds
        },
        config.s_validate_set_acc_json_path
    )

    ### get additional
    d_avg_fold_results = reporter.result_averaged_over_folds(
        l_fold_test_basic_res
    )

    reporter.produce_overall(
        config,
        l_y_gt_overall, l_y_predict_overall,
        d_avg_fold_results
    )
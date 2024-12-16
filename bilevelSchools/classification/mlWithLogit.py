from sklearn.model_selection import StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
import pandas as pd, numpy as np

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
    fold_splitter = StratifiedKFold(n_splits = config.i_num_folds, shuffle = True)
    l_y_gt_overall        = []
    l_y_predict_overall   = []
    l_fold_test_basic_res = []
    i_fold_idx = 1
    for l_train_validate_idx, l_test_idx in fold_splitter.split(df_features, l_y_all):


        ### Get Train Info
        df_X_train = df_features.iloc[l_train_validate_idx]
        l_y_train  = du.rebuild_list_with_idx(l_y_all, l_train_validate_idx)


        ### Get Test Features / Labels
        df_X_test = df_features.iloc[l_test_idx]
        l_y_test  = du.rebuild_list_with_idx(l_y_all, l_test_idx)

        ### Transform Categorical Featureres
        df_X_train, df_X_test = featureProcessers.one_hot_encode_categorical_features(
            config,
            df_X_train,
            df_X_test
        )

        ### Transform Continuous and Discrete Features, not really necessary but hey
        df_X_train, df_X_test = featureProcessers.normalize_numerical_features(
            config,
            df_X_train,
            df_X_test
        )

        model = LogisticRegression(
            max_iter = config.i_logit_max_itr,
            multi_class = 'multinomial',
            C = config.f_logit_C
        ).fit(
            df_X_train, l_y_train
        )

        ### Evaluate Training Set
        l_y_train_pred = model.predict(df_X_train)
        a_y_train_pred_dist = model.predict_proba(df_X_train)
        _ = reporter.evaluate_with_common_metrics(
            config, l_y_train, l_y_train_pred, a_y_train_pred_dist, s_task_type = 'training'
        )

        ### Evaluate Test Set
        l_y_test_pred = model.predict(df_X_test)
        a_y_test_pred_dist = model.predict_proba(df_X_test)
        d_fold_basic_test_res = reporter.evaluate_with_common_metrics(
            config, l_y_test, l_y_test_pred, a_y_test_pred_dist, s_task_type = 'test'
        )
        l_fold_test_basic_res.append(d_fold_basic_test_res)


        ### append
        l_y_gt_overall += l_y_test
        l_y_predict_overall += l_y_test_pred.tolist()

        i_fold_idx += 1

    ### get additional
    d_avg_fold_results = reporter.result_averaged_over_folds(
        l_fold_test_basic_res
    )


    reporter.produce_overall(
        config,
        l_y_gt_overall, l_y_predict_overall,
        d_avg_fold_results
    )
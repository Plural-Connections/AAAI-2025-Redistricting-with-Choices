import copy

import pandas as pd, xgboost as xgb, numpy as np
from scipy.special import softmax
from sklearn.model_selection import train_test_split

from bilevelSchools.classification import createFeaturesAndLabels, featureProcessers
from bilevelSchools.utils import data_utils as du

def train_or_load_a_model_with_full_set(config):

    ### Decided to simply Load a pre-saved model
    if config.b_train_a_new_model_to_generate_instance:
        pass
    else:
        ml_model = du.loadPickle(config.s_ml_model_instance_gen_pickle_path)
        return ml_model

    ### Load training data
    l_features = du.loadJson(
        config.s_ml_features_json_path
    )
    df_X = pd.DataFrame(l_features)

    ### Labels
    l_y = du.loadJson(
        config.s_ml_labels_json_path
    )

    ### Split to Train and Validate, but we use full training data to train
    df_X_train, df_X_validate, l_y_train, l_y_validate = train_test_split(
        df_X, l_y,
        shuffle    = True,
        stratify   = l_y,
        train_size = config.f_training_ratio_in_train_validate
    )
    du.savePickle(
        df_X_train,
        config.s_ml_model_instance_gen_training_reference_pickle_path
    )


    ### Transform Categorical Featureres
    df_X_train, df_X_validate = featureProcessers.label_encode_categorical_features(
        config,
        df_X_train,
        df_X_validate
    )


    ### Transform Continuous and Discrete Features, not really necessary but hey
    df_X_train, df_X_validate = featureProcessers.normalize_numerical_features(
        config,
        df_X_train,
        df_X_validate
    )


    d_train_params = copy.deepcopy(config.d_xgboost_basic_params)
    d_train_params['num_class'] = len(set(l_y))


    dm_train    = xgb.DMatrix(df_X_train,    label = np.array(l_y_train),    enable_categorical = True)
    dm_validate = xgb.DMatrix(df_X_validate, label = np.array(l_y_validate), enable_categorical = True)


    ml_model = xgb.train(
        d_train_params, dm_train, config.i_num_rounds,
        evals = [(dm_train, 'train'), (dm_validate, 'valid')],
        early_stopping_rounds = config.i_early_stopping_round,
        verbose_eval = True
    )

    du.savePickle(
        ml_model,
        config.s_ml_model_instance_gen_pickle_path
    )

    return ml_model

def gen_student_actual_choices(config, model):

    ### Load reference data
    df_X_train_reference = du.loadPickle(
        config.s_ml_model_instance_gen_training_reference_pickle_path
    )


    ### Create all useful things
    d_dist = du.loadJson(config.s_travel_dist_json_path)
    d_time = du.loadJson(config.s_travel_time_json_path)

    d_instance = {}
    for d_student in config.l_students:

        ### Get features for this student, assume zoned school is changing
        l_features_change_schools = []
        for s_school_id_zoned in config.l_school_ids:
            d_1_student_feat = createFeaturesAndLabels.get_1_student_feature(
                config, d_dist, d_time, d_student, s_school_id_zoned
            )
            l_features_change_schools.append(
                d_1_student_feat
            )


        ### Form Data, df_X_pred is the feature matrices, based on chaging zoned school
        df_X_train = copy.deepcopy(df_X_train_reference)
        df_X_pred  = pd.DataFrame(l_features_change_schools)


        ### Transform Categorical Featureres
        _, df_X_pred = featureProcessers.label_encode_categorical_features(
            config,
            df_X_train,
            df_X_pred
        )

        ### Transform Continuous and Discrete Features, not really necessary but hey
        _, df_X_pred = featureProcessers.normalize_numerical_features(
            config,
            df_X_train,
            df_X_pred
        )


        ### Make model predict distribution for each assumed zoned school
        a_margin_raw = model.predict(
            xgb.DMatrix(df_X_pred, enable_categorical = True),
            output_margin = True,
        )
        l_dist = softmax(a_margin_raw, axis = 1)


        ### figured out what school he/she goes to if he/she assigned to s_school_id_zoned
        d_student_go_to = {}
        for s_school_id_zoned, l_dist_1_zoned_school in zip(config.l_school_ids, l_dist):

            ### this is the assumption we used in the paper
            if d_student['zoned_school'] == s_school_id_zoned:
                s_school_id_goto = d_student['actual_school']
            else:
                s_school_id_goto = np.random.choice(
                    config.l_school_ids,
                    1,
                    p = l_dist_1_zoned_school
                )[0]

            d_student_go_to[s_school_id_zoned] = s_school_id_goto

        ### attached to instance
        d_instance[d_student['student_id']] = d_student_go_to

    return d_instance
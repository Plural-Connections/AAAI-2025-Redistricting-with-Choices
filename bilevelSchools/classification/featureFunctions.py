import math


def get_personal_ml_features(config, d_student):


    d_features = {
        "categorical": ["race"],
        "ordinal": ["grade"],
        "binary": [
            'has_elementary_siblings', 'went_to_same_school_with_sibling',
            'newly_joined_student', 'went_to_multiple_schools_before',
            'has_opt_out_before', 'has_opt_out_to_magnet_before'
        ]
    }

    d_features_with_values = {}
    for s_feat_type in d_features:
        for s_feat_name in d_features[s_feat_type]:
            config.record_a_feature_type(s_feat_name, s_feat_type)
            d_features_with_values[s_feat_name] = d_student[s_feat_name]

    return d_features_with_values

def get_census_ml_features(config, d_student):

    d_cb = config.d_cbs[d_student['census_block']]

    d_features = {
        "discrete": [
            'total_students_in_cb'
        ] + [
            s_race
            for s_race in config.l_races
        ],
        "continuous": [
            'ratio_students_in_cb'
        ] + [
            'ratio_{}_in_this_cb'.format(s_race)
            for s_race in config.l_races
        ] + [
            'ratio_{}_this_cb_over_whole_study'.format(s_race)
            for s_race in config.l_races
        ],
        "ordinal": ['ses_level']
    }

    d_features_with_values = {}
    for s_feat_type in d_features:
        for s_feat_name in d_features[s_feat_type]:
            config.record_a_feature_type(s_feat_name, s_feat_type)
            d_features_with_values[s_feat_name] = d_cb[s_feat_name]

    return d_features_with_values


def get_school_ml_features(config, d_dist, d_time, d_student, s_school_id_zoned):


    ### get features from each school
    d_all_school_features = {}
    for s_school_id in config.l_school_ids:

        d_1_school_fixed_features = format_1_school_fixed_feature(
            config, s_school_id, d_dist, d_time, d_student
        )

        d_all_school_features.update(d_1_school_fixed_features)

    d_1_school_dynamic_features = format_1_school_dynamic_feature(
        config, s_school_id_zoned
    )
    d_all_school_features.update(d_1_school_dynamic_features)

    return d_all_school_features


def format_1_school_fixed_feature(config, s_school_id, d_dist, d_time, d_student):


    d_school_feat = {}

    ### Travel Time Related
    d_school_feat['time_min'] = round(
        d_time[d_student['census_block']][s_school_id]
        /
        60,
        2
    )
    if math.isnan(d_school_feat['time_min']):
        d_school_feat['time_min'] = 1000


    ### Travel Distance Related
    d_school_feat['dist_km'] = round(
        d_dist[d_student['census_block']][s_school_id]
        /
        1000,
        2
    )
    if math.isnan(d_school_feat['dist_km']):
        d_school_feat['dist_km'] = 1000


    ### class info
    d_school_feat['is_magnet'] = int('Magnet' in config.d_schools[s_school_id]['Sub_Class'])

    d_features = {
        "binary": [
            'is_magnet'.format(s_school_id)
        ],
        "continuous": [
            'time_min', 'dist_km'
        ]
    }

    ### Add school id infront of each feature
    d_features_with_values = {}
    for s_feat_type in d_features:
        for s_feat_name in d_features[s_feat_type]:
            s_full_feat_name = '{}_{}'.format(s_school_id, s_feat_name)
            config.record_a_feature_type(s_full_feat_name, s_feat_type)
            d_features_with_values[s_full_feat_name] = d_school_feat[s_feat_name]

    return d_features_with_values


def format_1_school_dynamic_feature(config, s_school_id_zoned):

    d_feat_all_school = {
        'dy_zoned_school': s_school_id_zoned
    }
    d_school_zoned = config.d_schools[s_school_id_zoned]
    config.record_a_feature_type('dy_zoned_school', 'categorical')

    ### Zone of Choice
    for s_zoc_id in config.l_zone_of_choices:
        s_feat_name = 'dy_zoc_{}'.format(s_zoc_id)
        d_feat_all_school[s_feat_name] = int(
            s_zoc_id in d_school_zoned['zone_of_choice_ids']
        )
        config.record_a_feature_type(s_feat_name, 'binary')


    for s_school_id_itr in config.l_school_ids:

        d_school_itr = config.d_schools[s_school_id_itr]


        ### Check if the zoned school is in the same zoc compared to the itr school
        s_feat_name = 'same_zoc_with_{}'.format(s_school_id_itr)
        d_feat_all_school[s_feat_name] = int(
            len(
                set(d_school_zoned['zone_of_choice_ids']).intersection(
                    set(d_school_itr['zone_of_choice_ids'])
                )
            ) >= 1
        )
        config.record_a_feature_type(s_feat_name, 'binary')


        ### School rating features
        for s_ratio_term in ['gs_overall_rating', 'gs_test_rating', 'gs_progress_rating', 'gs_equity_rating']:
            s_feat_name = '{}_over_zoned_{}'.format(s_school_id_itr, s_ratio_term)
            d_feat_all_school[s_feat_name] = (
                d_school_itr[s_ratio_term] / d_school_zoned[s_ratio_term]
            )
            config.record_a_feature_type(s_feat_name, 'continuous')

    return d_feat_all_school


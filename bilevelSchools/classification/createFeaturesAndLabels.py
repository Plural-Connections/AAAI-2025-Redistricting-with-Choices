from bilevelSchools.classification import featureFunctions
from bilevelSchools.utils import data_utils as du

def create(config):

    config._init_feature_type_list()

    ### Create all useful things
    d_dist = du.loadJson(config.s_travel_dist_json_path)
    d_time = du.loadJson(config.s_travel_time_json_path)


    ### Iterate
    l_features = []
    l_labels   = []
    for d_student in config.l_students:

        d_1_student_feat = get_1_student_feature(
            config, d_dist, d_time, d_student, d_student['zoned_school']
        )

        assert(config.i_num_features == len(d_1_student_feat.keys()))

        l_features.append(
            d_1_student_feat
        )
        l_labels.append(
            get_1_student_label(config, d_student)
        )

    save_features(config, l_features, l_labels)


def get_1_student_label(config, d_student):
    return config.d_nces2idx[d_student['actual_school']]


### s_school_id_zoned is critical, because we keep changing this value in "generate instance" section
def get_1_student_feature(
    config, d_dist, d_time, d_student, s_school_id_zoned
):

    d_personal_features = featureFunctions.get_personal_ml_features(config, d_student)
    d_census_features   = featureFunctions.get_census_ml_features(config, d_student)
    d_school_features   = featureFunctions.get_school_ml_features(config, d_dist, d_time, d_student, s_school_id_zoned)

    return {
        **d_personal_features,
        **d_census_features,
        **d_school_features
    }


def save_features(config, l_features, l_labels):

    du.saveJson(
        l_features,
        config.s_ml_features_json_path
    )

    du.saveJson(
        l_labels,
        config.s_ml_labels_json_path
    )

    config.save_feature_collection()

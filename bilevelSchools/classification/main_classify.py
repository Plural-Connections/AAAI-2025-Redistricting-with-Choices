import sys

from bilevelSchools.classification import (
    createFeaturesAndLabels,
    mlWithLogit,
    mlWithXGB,
    simpleBaseline, ruleBased
)

def run_classify_pipeline(config):

    if config.b_preprocess_classification_input:
        createFeaturesAndLabels.create(config)

        ### usually handle features separately
        sys.exit()
    else:
        config.load_feature_collection()

    # in this baseline we assume the model simply predict a student will go to his / her zoned school
    if config.s_classify_method == 'follow':
        simpleBaseline.run(config)
    elif config.s_classify_method == 'rule_based':
        ruleBased.run(config)
    elif config.s_classify_method == 'multinomial_logit':
        mlWithLogit.classify(config)
    elif config.s_classify_method == 'xgboost':
        mlWithXGB.classify(config)
    else:
        raise ValueError('Wrong Classify Method')
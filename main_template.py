if __name__ == '__main__':

    ### Initailize everything
    from bilevelSchools.configuration import configuration
    config = configuration.Config()

    ### Preprocess Key Data
    from bilevelSchools.prepare import main_prepare
    main_prepare.run_prepare_pipeline(config)
    config._load_key_data()

    ### Machine Learning Section
    from bilevelSchools.classification import main_classify
    main_classify.run_classify_pipeline(config)

    ### Generate Instance Section
    from bilevelSchools.instance import main_generate
    main_generate.run_generate_instance_pipeline(config)

    ### Rezoning
    from bilevelSchools.rezone import main_rezone
    main_rezone.run_rezone_pipeline(config)
if __name__ == '__main__':

    ### Initailize everything
    from bilevelSchools.configuration import configuration
    config = configuration.Config()
    config._load_key_data()

    ### Preprocess Key Data
    from bilevelSchools.classification import main_classify
    main_classify.run_classify_pipeline(config)
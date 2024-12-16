if __name__ == '__main__':

    ### Initailize everything
    from bilevelSchools.configuration import configuration
    config = configuration.Config()
    config._load_key_data()

    ### Preprocess Key Data
    from bilevelSchools.rezone import main_rezone
    main_rezone.run_rezone_pipeline(config)
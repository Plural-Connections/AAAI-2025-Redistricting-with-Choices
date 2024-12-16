if __name__ == '__main__':

    ### Initailize everything
    from bilevelSchools.configuration import configuration
    config = configuration.Config()
    config._load_key_data()

    ### Preprocess Key Data
    from bilevelSchools.analzye import main_analyze
    main_analyze.run_analyze_pipeline(config)
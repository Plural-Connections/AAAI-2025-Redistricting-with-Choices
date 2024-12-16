if __name__ == '__main__':

    ### Initailize everything
    from bilevelSchools.configuration import configuration
    config = configuration.Config()

    ### Preprocess Key Data
    from bilevelSchools.prepare import main_prepare
    main_prepare.run_prepare_pipeline(config)
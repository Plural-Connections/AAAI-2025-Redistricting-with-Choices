if __name__ == '__main__':

    ### Initailize everything
    from bilevelSchools.configuration import configuration
    config = configuration.Config()
    config._load_key_data()

    ### Generate Instance Section
    from bilevelSchools.instance import main_generate
    main_generate.run_generate_instance_pipeline(config)
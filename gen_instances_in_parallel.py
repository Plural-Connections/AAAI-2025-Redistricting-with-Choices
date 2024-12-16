if __name__ == '__main__':

    ### Initailize everything
    from bilevelSchools.configuration import configuration
    config = configuration.Config()
    config._load_key_data()

    ### Make sure these things are loaded
    config.b_train_a_new_model_to_generate_instance = False
    config.b_only_train_a_model = False


    ### Generate Instance Section
    from bilevelSchools.instance import main_generate
    main_generate.run_generate_instance_pipeline(config, i_instance_idx = config.i_instance_idx)
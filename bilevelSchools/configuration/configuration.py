import os, argparse

from bilevelSchools.utils import data_utils as du


class Config:

    def __init__(self):

        self.s_config_dir = os.path.dirname(__file__)

        self._load_parameters()

    def _load_parameters(self):

        # start to process all input arguments
        s_args_dir = os.path.join(
            self.s_config_dir,
            "args_with_default_values"
        )

        l_all_input_arguments = [
            d_1_input_arg
            for s_file_name in os.listdir(
                s_args_dir
            )
            if s_file_name.endswith('.yaml')
            for d_1_input_arg in du.loadYaml(
                os.path.join(s_args_dir, s_file_name)
            )
        ]

        # now load input file, this input file has priority, it can overwrite the input from --
        parser_basic = argparse.ArgumentParser()
        parser_basic.add_argument(
            '--s_input_dir_par_yaml_path',
            required = False,
            type = str,
            default = os.path.join(
                self.s_config_dir,
                'place_holder.yaml'
            )
        )
        self.d_input_args_from_user_yaml = du.loadYaml(
            vars(parser_basic.parse_known_args()[0])[
                's_input_dir_par_yaml_path'
            ]
        )


        ### try to load user's input args, if the user does not send an input using the yaml file, then use default value
        parser = argparse.ArgumentParser()
        self.d_args_dirs  = {
            d_1_arg['arg_name']: d_1_arg
            for d_1_arg in l_all_input_arguments if d_1_arg['input_kind'] == 'dir'
        }
        self.d_args_paths = {
            d_1_arg['arg_name']: d_1_arg
            for d_1_arg in l_all_input_arguments if d_1_arg['input_kind'] == 'path'
        }
        self.d_args_pars = {
            d_1_arg['arg_name']: d_1_arg
            for d_1_arg in l_all_input_arguments if d_1_arg['input_kind'] == 'par'
        }


        ### start to parse all input arguments
        for d_1_arg in l_all_input_arguments:

            ### For each argument, figure out defualt value, and its type
            # Type: regular input parameters, such as convex optimization factor
            if d_1_arg["input_kind"] == "pars":
                arg_val_default = d_1_arg["default_val"]
                var_type = du.str2bool if type(arg_val_default) == bool else type(d_1_arg["default_val"])

            # Other Type: directories or paths
            else:
                arg_val_default = d_1_arg["default_val"]
                var_type = type(d_1_arg["default_val"])


            ### For each argument, check if the user have some input using the input yaml file
            if d_1_arg['arg_name'] in self.d_input_args_from_user_yaml:

                arg_value_user_yaml = self.d_input_args_from_user_yaml[d_1_arg['arg_name']]
                assert(
                    type(arg_val_default) == type(arg_value_user_yaml)
                )

                arg_val_to_parser = arg_value_user_yaml
            else:
                arg_val_to_parser = arg_val_default


            ### add this argument to parser
            parser.add_argument(
                "--" + d_1_arg["arg_name"],
                required = False,
                nargs = d_1_arg["nargs"],
                type = var_type,
                default = arg_val_to_parser
            )

        ### now we have all input arguments, "--" can further overwrite the settings in yaml file
        self.d_final_input_args_from_user = vars(parser.parse_known_args()[0])

        ### now we need construct all directories
        self._finalize_dirs()

        ### now we need to construct all paths
        self._finalize_paths()

        ### now we need to finalize all other pars
        self._finalize_pars()


    def _finalize_dirs(self):

        # connect dirs
        for s_dir_name in self.d_args_dirs:

            final_directory_from_user = self._get_final_value_from_user(s_dir_name)

            if os.path.isabs(final_directory_from_user):
                final_directory_value = final_directory_from_user
            else:
                final_directory_value = os.path.join(
                    os.getenv('HOME'),
                    final_directory_from_user
                )

            du.checkDir(final_directory_value)

            self.d_args_dirs[s_dir_name]['final_value'] = final_directory_value

            setattr(self, s_dir_name, final_directory_value)


    def _finalize_paths(self):

        # connect paths
        for s_path_name in self.d_args_paths:

            final_path_from_user = self._get_final_value_from_user(s_path_name)

            if os.path.isabs(final_path_from_user):
                final_path_value = final_path_from_user
            else:
                d_1_path_arg = self.d_args_paths[s_path_name]
                ### get the parent directory of this file
                s_parent_dir = self.d_args_dirs[
                    d_1_path_arg['parent_dir']
                ]['final_value']

                ### connect the file to the parent directory
                final_path_value = os.path.join(
                    s_parent_dir,
                    final_path_from_user
                )

            setattr(self, s_path_name, final_path_value)


    def _finalize_pars(self):
        for s_par_name in self.d_args_pars:
            final_value_from_user = self._get_final_value_from_user(s_par_name)
            setattr(self, s_par_name, final_value_from_user)


    def _get_final_value_from_user(self, s_arg_name):
        final_value_from_user = self.d_final_input_args_from_user[s_arg_name]
        return final_value_from_user


    def _load_key_data(self):
        self._load_cb_data()
        self._load_school_data()
        self._load_student_data()

    def _load_school_data(self):
        ### school related
        self.d_schools = du.loadJson(
            self.s_school_features_json_path
        )
        self.l_schools = list(self.d_schools.values())
        self.l_school_ids = [
            d_school['nces_id']
            for d_school in self.l_schools
        ]

        self.d_idx2nces = {
            i: self.l_school_ids[i]
            for i in range(len(self.l_school_ids))
        }
        self.d_nces2idx = {
            self.l_school_ids[i]: i
            for i in range(len(self.l_school_ids))
        }


    def _load_student_data(self):
        ### student related
        self.l_students = du.loadJson(
            self.s_student_features_json_path
        )

    def _load_cb_data(self):
        ### Census block related
        self.d_cbs = du.loadJson(self.s_cb_features_json_path)
        self.l_cb_ids = list(self.d_cbs.keys())

        self.i_lowses_population = sum(
            self.d_cbs[s_cb_id]['total_students_in_cb']
            for s_cb_id in self.l_cb_ids
            if self.d_cbs[s_cb_id]['ses_level'] == 0
        )

    def _init_feature_type_list(self):

        self.d_feature_collection = {
            "categorical": [],
            "continuous": [],
            "discrete": [],
            "ordinal": [],
            'binary': []
        }
        self.i_num_features = 0

    def record_a_feature_type(self, s_feat_name, s_feat_type):

        if s_feat_type in self.d_feature_collection.keys():
            if s_feat_name in self.d_feature_collection[s_feat_type]:
                pass
            else:
                self.d_feature_collection[s_feat_type].append(s_feat_name)
                self.i_num_features += 1
        else:
            raise ValueError('Wrong Type of Feature')

    def save_feature_collection(self):
        du.saveJson(
            self.d_feature_collection,
            self.s_ml_features_collection_json_path
        )

    def load_feature_collection(self):
        self.d_feature_collection = du.loadJson(
            self.s_ml_features_collection_json_path
        )

        self.i_num_features = sum(
            [
                len(self.d_feature_collection[s_feat_type])
                for s_feat_type in self.d_feature_collection.keys()
            ]
        )

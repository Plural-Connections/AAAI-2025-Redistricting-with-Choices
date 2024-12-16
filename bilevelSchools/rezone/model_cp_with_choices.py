import time, sys

import numpy as np, networkx as nx
from ortools.sat.python import cp_model

from bilevelSchools.rezone import model_cp_nces_main
from bilevelSchools.utils import data_utils as du

class OptimizationModel(model_cp_nces_main.OptimizationModel):

    def __init__(self, config):

        super().__init__(config)
        self._construct_model(config)


    def _construct_model(self, config):

        f_start_time = time.time()
        self.model = cp_model.CpModel()
        self._select_instances(config)
        self._create_vars(config)
        self._create_constraints(config)
        self._set_objective(config)
        f_end_time = time.time()
        i_sec_construct = round(
            f_end_time - f_start_time, 0
        )
        du.print_key_msg(
            'Took {} seconds to create the CP Model'.format(i_sec_construct)
        )


    def _create_vars(self, config):

        self.x = {}
        self.y = {}
        for s_cb_id in config.l_cb_ids:

            ### Get the zoned school / and nces's corresponding integer value
            s_school_id_zoned  = config.d_cbs[s_cb_id]['zoned_school']
            i_school_idx_zoned = config.d_nces2idx[s_school_id_zoned]


            ### Integer Variable
            # s_cb_id is mapped to a shcool (int value not nces id)
            # the additional variable used in this model
            self.y[s_cb_id] = self.model.NewIntVar(
                min(config.d_idx2nces.keys()),
                max(config.d_idx2nces.keys()),
                "{}_decision".format(
                    s_cb_id
                )
            )

            # initial solution for y
            self.model.AddHint(
                self.y[s_cb_id],
                i_school_idx_zoned
            )


            ### Binary Variable
            # if s_school_id is assigned to s_cb_id
            self.x[s_cb_id] = {}
            for s_school_id in config.l_school_ids:

                i_school_idx = config.d_nces2idx[s_school_id]

                self.x[s_cb_id][i_school_idx] = self.model.NewBoolVar(
                    "{}_assign_to_{}".format(
                        s_cb_id, i_school_idx
                    )
                )

                 ### initial solution for x
                if s_school_id == s_school_id_zoned:
                    self.model.AddHint(
                        self.x[s_cb_id][i_school_idx],
                        True
                    )
                else:
                    self.model.AddHint(
                        self.x[s_cb_id][i_school_idx],
                        False
                    )

    def _create_constraints(self, config):

        for s_cb_id in config.l_cb_ids:
            self._add_cst_link_x_y(config, s_cb_id)
            self._add_cst_travel(config, s_cb_id)


        for i_instance_idx in self.l_selected_instances_idx:
            d_student_choices = du.loadJson(
                config.s_1_choice_instance_json_path.format(i_instance_idx)
            )
            print('Loaded {} to create constraint'.format(config.s_1_choice_instance_json_path.format(i_instance_idx)))
            for s_school_id in config.l_school_ids:
                self._add_cst_school_population_stay_resonable(config, d_student_choices, s_school_id)

        for s_school_id in config.l_school_ids:
            if config.b_add_contiguity_cst:
                du.print_key_msg('Adding Contiguity Constraints for School {}'.format(s_school_id))
                self._add_cst_contiguity(config, s_school_id)


    def _add_cst_link_x_y(self, config, s_cb_id):

        for s_school_id in config.l_school_ids:

            i_school_idx = config.d_nces2idx[s_school_id]

            self.model.Add(
                self.y[s_cb_id] == i_school_idx
            ).OnlyEnforceIf(
                self.x[s_cb_id][i_school_idx]
            )

            self.model.Add(
                self.y[s_cb_id] != i_school_idx
            ).OnlyEnforceIf(
                self.x[s_cb_id][i_school_idx].Not()
            )


    def _add_cst_travel(self, config, s_cb_id):


        ### Compute travel time bound
        s_school_id_zoned = config.d_cbs[s_cb_id]['zoned_school']
        if np.isnan(
            self.d_car_time[s_cb_id][s_school_id_zoned]
        ):
            pass
        else:
            f_max_allowed_travel_time = int(
                config.i_scale_up_multip
                *
                np.round(
                    (1 + config.f_travel_time_increase_max_ratio)
                    *
                    self.d_car_time[s_cb_id][s_school_id_zoned],
                    decimals = config.i_num_decimal,
                )
            )

        ### Start to add constraint
        for s_school_id in config.l_school_ids:

            i_school_idx = config.d_nces2idx[s_school_id]

            ### data unavailable, so cannot assign this cb to this school
            if np.isnan(
                self.d_car_time[s_cb_id][s_school_id]
            ):
                if s_school_id == s_school_id_zoned:
                    self.model.Add(
                        self.x[s_cb_id][i_school_idx] == True
                    )
                    self.model.Add(
                        self.y[s_cb_id] == i_school_idx
                    )
                else:
                    self.model.Add(
                        self.x[s_cb_id][i_school_idx] == False
                    )
                    self.model.Add(
                        self.y[s_cb_id] != i_school_idx
                    )

            else:

                if s_school_id == s_school_id_zoned:
                    pass
                else:
                    f_new_travel_time = int(
                        config.i_scale_up_multip
                        *
                        np.round(
                            self.d_car_time[s_cb_id][s_school_id],
                            decimals = config.i_num_decimal,
                        )
                    )

                    ### this schools is too far for this cb, don't rezone the cb to it
                    if f_new_travel_time > f_max_allowed_travel_time:
                        self.model.Add(
                            self.x[s_cb_id][i_school_idx] == False
                        )
                        self.model.Add(
                            self.y[s_cb_id] != i_school_idx
                        )

    def _add_cst_school_population_stay_resonable(self, config, d_student_choices, s_school_id_focus):


        ### After rezoned, a school's population should be bounded by the following two values
        i_new_population_max = int(
            config.i_scale_up_multip
            *
            np.round(
                (1 + config.f_school_population_change_max_ratio)
                *
                self.d_school_pops_current[s_school_id_focus]["total"],
                decimals = config.i_num_decimal
            )
        )
        i_new_population_min = int(
            config.i_scale_up_multip
            *
            np.round(
                (1 - config.f_school_population_change_max_ratio)
                *
                self.d_school_pops_current[s_school_id_focus]["total"],
                decimals = config.i_num_decimal
            )
        )


        l_population_this_school = []
        for d_student in config.l_students:

            ### basic info
            s_student_id    = d_student['student_id']
            s_cb_id_student = d_student['census_block']

            ### this student will go to s_school_id_focus if he / she is zoned to certain schools
            for s_school_id in config.l_school_ids:
                if d_student_choices[s_student_id][s_school_id] == s_school_id_focus:
                    i_school_idx = config.d_nces2idx[s_school_id]
                    l_population_this_school.append(
                        self.x[s_cb_id_student][i_school_idx] * 1
                    )

        new_population = (
            config.i_scale_up_multip
            *
            sum(l_population_this_school)
        )

        ### Bound this New Value
        self.model.Add(
            new_population <= i_new_population_max
        )
        self.model.Add(
            new_population >= i_new_population_min
        )


    def _add_cst_contiguity(self, config, s_school_id):


        ### load neighbor information
        d_cb_original_zoned_neighbors = du.loadJson(
            config.s_cb_neighbor_json_path
        )

        ### Get the graph based on this particular school
        graph_nces = self.d_nces_graphs[s_school_id]
        l_node_ids = graph_nces.nodes()

        # each element: [id, {info}], also, we can use id to query info
        node_data = graph_nces.nodes(data = True)

        ### This is the cb related to the school, call it ROOT, [0] is safe to use because each school only has 1 such cb
        i_cb_id_root = [
            i_node_id
            for i_node_id, d_node_info in node_data
            if d_node_info['attrs']['dist_from_root'] == 0
        ][0]

        ### get islands
        set_already_island_cbs = set(
            filter(
                lambda i_node_id: node_data[i_node_id]['is_island_wrt_orig_school'] == 1,
                l_node_ids
            )
        )


        ### get important cbs
        l_cb_ids_to_enforce_contiguity = list(
            (
                l_node_ids - {i_cb_id_root} - set_already_island_cbs
            )
        )

        i_school_idx = config.d_nces2idx[s_school_id]
        for i_cb_id in l_cb_ids_to_enforce_contiguity:


            ### now working with s_cb_id, there are a few neighbouring cbs that are closer to the root
            set_ngbh_cbs_closer_to_school = model_cp_nces_main.get_neighbors_closer_to_school(graph_nces, node_data, i_cb_id)


            ### if we are dealing with the original zoned school of this cb
            if node_data[i_cb_id]['attrs']['orig_school_id'] == int(s_school_id):

                set_cb_zoned_school_neighbors = set(d_cb_original_zoned_neighbors[str(i_cb_id)])

                i_curr_len = len(
                    set_cb_zoned_school_neighbors.intersection(set_ngbh_cbs_closer_to_school)
                )

                if i_curr_len == 0:

                    nodes_assigned_to_school = list(
                        filter(
                            lambda x: (
                                node_data[x]["attrs"]["orig_school_id"] == int(s_school_id)
                                and
                                node_data[x]["is_island_wrt_orig_school"] != 1
                            ),
                            l_node_ids,
                        )
                    )

                    graph_sub = graph_nces.subgraph(nodes_assigned_to_school)
                    for n in nodes_assigned_to_school:
                        try:
                            sp_length = nx.shortest_path_length(
                                graph_sub, source = n , target = i_cb_id_root
                            )
                            node_data[n]["attrs"]["dist_from_root"] = sp_length
                        except:
                            continue

                    set_ngbh_cbs_closer_to_school = set(
                        model_cp_nces_main.get_neighbors_closer_to_school(graph_sub, node_data, i_cb_id)
                    )

            ### Add constraint
            self.model.Add(
                sum(
                    self.x[str(n)][i_school_idx]
                    for n in set_ngbh_cbs_closer_to_school
                ) > 0
            ).OnlyEnforceIf(
                self.x[str(i_cb_id)][i_school_idx]
            )


    def _set_objective(self, config):

        # dissimilarities, summaation over schools
        l_school_dissimilarity_all_instances = []

        # start to iterate instance
        for i_instance_idx in self.l_selected_instances_idx:

            d_student_choices = du.loadJson(
                config.s_1_choice_instance_json_path.format(i_instance_idx)
            )
            print('Loaded {} to construct objective function'.format(config.s_1_choice_instance_json_path.format(i_instance_idx)))

            # start to iterate schools
            for s_school_id_focus in config.l_school_ids:

                l_school_target_population = []
                l_school_total_population  = []

                ### linexpally compute the number of students in each school
                for d_student in config.l_students:

                    ### basic info
                    s_student_id    = d_student['student_id']
                    s_cb_id_student = d_student['census_block']

                    ### this student will go to s_school_id_focus if he / she is zoned to certain schools
                    for s_school_id in config.l_school_ids:
                        if d_student_choices[s_student_id][s_school_id] == s_school_id_focus:
                            i_school_idx = config.d_nces2idx[s_school_id]

                            l_school_total_population.append(
                                self.x[s_cb_id_student][i_school_idx] * 1
                            )

                            if config.d_cbs[s_cb_id_student]['ses_level'] == 0:
                                l_school_target_population.append(
                                    self.x[s_cb_id_student][i_school_idx] * 1
                                )


                ### sum linexp, and scaling
                var_school_target_population = self.model.NewIntVar(
                    0, config.i_scale_up_multip ** 2, "instance_{}_school_{}_target_type_population".format(i_instance_idx, s_school_id_focus)
                )
                self.model.Add(
                    var_school_target_population
                    ==
                    config.i_scale_up_multip * sum(l_school_target_population)
                )

                var_school_nontarget_population = self.model.NewIntVar(
                    0, config.i_scale_up_multip ** 2, "instance_{}_school_{}_nontarget_type_population".format(i_instance_idx, s_school_id_focus)
                )
                self.model.Add(
                    var_school_nontarget_population
                    ==
                    config.i_scale_up_multip * (sum(l_school_total_population) - sum(l_school_target_population))
                )


                ### Scaling and prepping to apply division equality constraint,
                # required to do divisions in CP-SAT
                # Fraction: cat students that are at this school / cat students over the whole study
                var_ratio_at_school_target_type = self.model.NewIntVar(
                    0, config.i_scale_up_multip ** 2, "instance_{}_school_{}_target_type_ratio".format(i_instance_idx, s_school_id_focus)
                )
                self.model.AddDivisionEquality(
                    # Quotient
                    var_ratio_at_school_target_type,

                    # nom
                    var_school_target_population,

                    # denom
                    self.d_category_population['low_ses']
                )


                ### similar
                # Fraction of non-cat students that are at this school
                var_ratio_at_school_nontarget_type = self.model.NewIntVar(
                    0, config.i_scale_up_multip ** 2, "instance_{}_school_{}_nontarget_type_ratio".format(i_instance_idx, s_school_id_focus)
                )
                self.model.AddDivisionEquality(
                    # Quotient
                    var_ratio_at_school_nontarget_type,

                    # nom
                    var_school_nontarget_population,

                    # denom
                    self.d_category_population["total"] - self.d_category_population['low_ses'],
                )


                ### Computing dissimilarity
                var_diff_val = self.model.NewIntVar(
                    -1 * (config.i_scale_up_multip),
                    config.i_scale_up_multip ** 2,
                    "instance_{}_school_{}_ratio_difference".format(i_instance_idx, s_school_id_focus)
                )
                self.model.Add(
                    var_diff_val == var_ratio_at_school_target_type - var_ratio_at_school_nontarget_type
                )

                var_dissimilarity_school = self.model.NewIntVar(
                    0, config.i_scale_up_multip ** 2, "instance_{}_school_{}_dissimilarity".format(i_instance_idx, s_school_id_focus)
                )

                # var_obj_term_to_add = absolute(var_diff_val)
                self.model.AddAbsEquality(
                    # lhs of the equation
                    var_dissimilarity_school,

                    # rhs of the equation but with a abs
                    var_diff_val
                )

                l_school_dissimilarity_all_instances.append(var_dissimilarity_school)

        self.model.Minimize(sum(l_school_dissimilarity_all_instances))


    ### Solve the CP Model and Report Result
    def solve(self, config, evaluator):

        du.print_key_msg('Start to Compute')
        self.solver = cp_model.CpSolver()

        # set basic
        self.solver.parameters.max_time_in_seconds = config.i_cp_max_solving_hour * 3600
        self.solver.parameters.num_search_workers  = config.i_cp_num_threads


        s_status = self.solver.Solve(self.model)
        print('The Status of this CP model is "{}"'.format(s_status))
        if s_status == cp_model.OPTIMAL:
            s_status = 'Optimal'
        elif s_status == cp_model.FEASIBLE:
            s_status = 'Feasible'
        else:
            s_status = 'Failed...'
            sys.exit()

        d_school_assignment = {
            # get result for cb
            s_cb_id: self.solver.Value(
                self.y[s_cb_id]
            )
            for s_cb_id in config.l_cb_ids
        }

        ### Get summary result
        d_cp_summary = {
            'solver': 'ortools',
            'obj_solver': self.solver.ObjectiveValue() / config.i_scale_up_multip,
            'obj_evaluator': evaluator.evalute_objective(config, d_school_assignment),
            'solving_time_limit_hour': config.i_cp_max_solving_hour,
            'solving_time': self.solver.WallTime(),
            'num_branch': self.solver.NumBranches(),
            'num_conflicts': self.solver.NumConflicts(),
            'status': s_status
        }

        du.saveJson(
            d_cp_summary,
            config.s_result_cp_summary_json_path.format(config.i_cp_max_solving_hour)
        )

        return d_school_assignment
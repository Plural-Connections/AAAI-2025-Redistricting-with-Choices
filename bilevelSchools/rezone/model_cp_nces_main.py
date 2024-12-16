import random

from bilevelSchools.prepare.parseCensusBlockNeighbor import prep_blocks_networks
from bilevelSchools.utils import data_utils as du

class OptimizationModel():

    def __init__(self, config):

        self._select_instances(config)
        self._load_key_data(config)


    def _select_instances(self, config):

        random.seed(config.i_random_seed_for_picking_instances)
        self.l_selected_instances_idx = random.sample(
            range(1, config.i_num_possible_instances + 1),
            config.i_num_instances
        )
        print('The instances used here are {}'.format(self.l_selected_instances_idx))


    def _load_key_data(self, config):

        ### car travel time
        # Format self.d_car_time[s_cb_id][s_school_id]
        self.d_car_time = du.loadJson(
            config.s_travel_time_json_path
        )

        ### each school has a seperate graph, saved as a json format
        # Example: d_nces_graphs[s_school_id] = some networkx graph
        self.d_nces_graphs = prep_blocks_networks(
            du.loadJson(
                config.s_cb_school_network_json_path
            )
        )

        ### Two dictionary for populations, and 1 constant
        # self.d_school_pops_current: each school's population, based on each category
        # self.d_cb_pops: each cb's population, based on each category
        self.d_school_pops_current = {
            s_school_id: {'low_ses': 0, 'total': 0}
            for s_school_id in config.l_school_ids
        }
        self.d_cb_pops = {
            s_cb_id: {'low_ses': 0, 'total': 0}
            for s_cb_id in config.l_cb_ids
        }
        for d_student in config.l_students:

            ### basic info
            s_cb_id_student = d_student['census_block']
            s_school_id_actual = d_student['actual_school']

            # we will study the dissimilarity of low ses_level and other ses_level
            if config.d_cbs[s_cb_id_student]['ses_level'] == 0:
                self.d_cb_pops[s_cb_id_student]['low_ses'] += 1
                self.d_school_pops_current[s_school_id_actual]['low_ses'] += 1

            # attach to total population
            self.d_cb_pops[s_cb_id_student]['total'] += 1
            self.d_school_pops_current[s_school_id_actual]['total'] += 1

        ### assert
        for s_cb_id in config.l_cb_ids:
            assert(
                config.d_cbs[s_cb_id]['total_students_in_cb'] == self.d_cb_pops[s_cb_id]['total']
            )
        for s_school_id in config.l_school_ids:
            assert(
                config.d_schools[s_school_id]['total_student_in_school'] == self.d_school_pops_current[s_school_id]['total']
            )

        ### Population for each Category
        du.print_key_msg('Here are the population of each category:')
        self.d_category_population = {}
        for s_cat_name in ['low_ses', 'total']:

            i_pop_from_school = sum(
                [
                    self.d_school_pops_current[s_school_id][s_cat_name]
                    for s_school_id in self.d_school_pops_current.keys()
                ]
            )

            i_pop_from_cb = sum(
                [
                    self.d_cb_pops[s_cb_id][s_cat_name]
                    for s_cb_id in self.d_cb_pops.keys()
                ]
            )

            self.d_category_population[s_cat_name] = i_pop_from_cb

            print(s_cat_name, i_pop_from_school, i_pop_from_cb)

            # make sure the previous part was correctly handled
            assert(
                i_pop_from_cb == i_pop_from_school
            )


def get_neighbors_closer_to_school(graph_school, all_nodes, i_cb_id):
    neighbors = graph_school.neighbors(i_cb_id)

    closer_neighbor_cbs = set(
        filter(
            lambda x: (
                all_nodes[x]["attrs"]["dist_from_root"]
                <
                all_nodes[i_cb_id]["attrs"]["dist_from_root"]
            ),
            neighbors
        )
    )

    return set([str(x) for x in closer_neighbor_cbs])
import statistics

import numpy as np

from bilevelSchools.rezone import model_cp_nces_main
from bilevelSchools.utils import data_utils as du

class solutionEvaluator(model_cp_nces_main.OptimizationModel):

    def __init__(self, config):

        super().__init__(config)


    ### This means we simply do a evaluation without optimization
    def _evaluate_current(self, config):

        d_school_assignment_current = {}
        for s_cb_id in config.l_cb_ids:

            ### Get the zoned school / and nces's corresponding integer value
            s_school_id_zoned = config.d_cbs[s_cb_id]["zoned_school"]
            s_sch_idx_zoned   = config.d_nces2idx[s_school_id_zoned]

            d_school_assignment_current[s_cb_id] = s_sch_idx_zoned

        _, f_obj_avg_default = self.evalute_objective(config, d_school_assignment_current)
        du.print_key_msg(
            'The Default Objective (i.e., do not rezone at all) is {}'.format(f_obj_avg_default)
        )
        return d_school_assignment_current


    def evalute_objective(self, config, d_school_assignment):

        l_obj_instances = [
            self.evalute_objective_1_instance(config, d_school_assignment, i_instance_idx)
            for i_instance_idx in self.l_selected_instances_idx
        ]

        f_obj_avg = round(
            sum(l_obj_instances) / len(l_obj_instances),
            4
        )

        du.saveJson(
            {
                "avg_score": f_obj_avg,
                "sum_score": sum(l_obj_instances),
                "scores": l_obj_instances
            },
            config.s_result_scores_json_path
        )

        return l_obj_instances, f_obj_avg


    def evalute_objective_1_instance(self, config, d_school_assignment, i_instance_idx):

        ### load the instance
        d_student_choices = du.loadJson(
            config.s_1_choice_instance_json_path.format(i_instance_idx)
        )
        print('Evalute Objective of Instance: {}'.format(config.s_1_choice_instance_json_path.format(i_instance_idx)))

        ###
        d_school_pops_actual = {
            s_school_id: {'low_ses': 0, 'total': 0}
            for s_school_id in config.l_school_ids
        }
        for d_student in config.l_students:

            ### basic info
            s_student_id    = d_student['student_id']
            s_cb_id_student = d_student['census_block']

            ### zoned information from optimzation result
            i_school_idx_zoned = d_school_assignment[s_cb_id_student]
            s_school_id_zoned  = config.d_idx2nces[i_school_idx_zoned]

            ### use the instance, get where the student actually go to
            s_school_id_actual = d_student_choices[s_student_id][s_school_id_zoned]

            ### assign student to school
            if config.d_cbs[s_cb_id_student]['ses_level'] == 0:
                d_school_pops_actual[s_school_id_actual]['low_ses'] += 1

            d_school_pops_actual[s_school_id_actual]['total'] += 1


        ### verify 2 values
        i_school_low_ses = sum(d_school_pops_actual[s_school_id]['low_ses'] for s_school_id in config.l_school_ids)
        i_school_total   = sum(d_school_pops_actual[s_school_id]['total']   for s_school_id in config.l_school_ids)
        assert(i_school_low_ses == self.d_category_population['low_ses'])
        assert(i_school_total   == self.d_category_population['total'])


        ### start to compute
        l_sch_objs = []
        for s_school_id in config.l_school_ids:

            # Fraction: this type of students that are at this school / this type of students over the whole study
            f_ratio_category = (
                d_school_pops_actual[s_school_id]['low_ses']
                /
                self.d_category_population['low_ses']
            )

            # similar stuff
            f_ratio_noncategory = (
                (d_school_pops_actual[s_school_id]['total'] - d_school_pops_actual[s_school_id]['low_ses'])
                /
                (self.d_category_population["total"] - self.d_category_population['low_ses'])
            )

            l_sch_objs.append(
                abs(f_ratio_category - f_ratio_noncategory)
            )

        return sum(l_sch_objs) / 2

    def load_saved_assignment(self, config):

        d_cb_result = du.loadJson(
            config.s_result_cb_json_path
        )

        d_school_assignment = {
            s_cb_id: config.d_nces2idx[d_cb_result[s_cb_id]['new_zoned_school']]
            for s_cb_id in config.l_cb_ids
        }

        self.evalute_objective(config, d_school_assignment)

        return d_school_assignment


    def report_results(self, config, d_school_assignment):


        self.report_result_cb_changes(config, d_school_assignment)

        l_student_stats_instances = []
        l_school_stats_instances  = []
        for i_instance_idx in self.l_selected_instances_idx:

            ### load the instance
            d_student_choices = du.loadJson(
                config.s_1_choice_instance_json_path.format(i_instance_idx)
            )
            print('Evalute Result {}'.format(config.s_1_choice_instance_json_path.format(i_instance_idx)))

            d_student_stats_instance, d_school_stats_instance = self.report_student_statistic(config, d_school_assignment, d_student_choices)

            l_student_stats_instances.append(d_student_stats_instance)
            l_school_stats_instances.append(d_school_stats_instance)

        self.create_student_statistic_files(config, l_student_stats_instances)
        self.create_school_statistic_files(config, l_school_stats_instances)


    def report_result_cb_changes(self, config, d_school_assignment):

        ### first result: each cb's status
        d_cb_result = {
            s_cb_id: {
                'old_zoned_school': config.d_cbs[s_cb_id]['zoned_school'],
                'new_zoned_school': None,
                'has_new_school': False,
                'travel_time_+-%': None
            }
            for s_cb_id in config.l_cb_ids
        }

        ### Start to process result for each cb
        for s_cb_id in config.l_cb_ids:

            # get result for cb
            i_school_idx_result = d_school_assignment[s_cb_id]
            s_school_id_result = config.d_idx2nces[i_school_idx_result]

            d_cb_result[s_cb_id]['new_zoned_school'] = s_school_id_result
            d_cb_result[s_cb_id]['has_new_school'] = bool(
                d_cb_result[s_cb_id]['old_zoned_school']
                !=
                d_cb_result[s_cb_id]['new_zoned_school']
            )

            ### compute change in travel time
            f_old_car_time = self.d_car_time[s_cb_id][config.d_cbs[s_cb_id]['zoned_school']]
            f_new_car_time = self.d_car_time[s_cb_id][s_school_id_result]
            # there is one 0.0 travel time in the data
            if np.isnan(f_old_car_time) or (f_old_car_time == 0.0):
                pass
            else:
                f_changing_ratio = (
                    f_new_car_time - f_old_car_time
                ) / f_old_car_time

                ## note that here we can reduing the travel time, but not increasing it too much
                assert(f_changing_ratio <= config.f_travel_time_increase_max_ratio)

                d_cb_result[s_cb_id]['travel_time_+-%'] = round(f_changing_ratio, 2)

        du.saveJson(
            d_cb_result,
            config.s_result_cb_json_path
        )

    def report_student_statistic(self, config, d_school_assignment, d_student_choices):

        ### initialize
        d_school_stats_instance = {
            s_school_id: {"students_low_ses": 0, "students_total": 0}
            for s_school_id in config.l_school_ids
        }

        i_rezoned_student_lowses = 0
        i_rezoned_student_total  = 0
        i_optout_student         = 0
        l_travel_time            = []
        for d_student in config.l_students:

            ### basic info
            s_student_id    = d_student['student_id']
            s_cb_id_student = d_student['census_block']


            ### get new rezoned school
            s_school_id_newzoned = config.d_idx2nces[d_school_assignment[s_cb_id_student]]
            s_school_id_newgoto  = d_student_choices[s_student_id][s_school_id_newzoned]
            if s_school_id_newzoned != s_school_id_newgoto:
                i_optout_student += 1


            ### add to school
            d_school_stats_instance[s_school_id_newgoto]['students_total'] += 1
            if config.d_cbs[s_cb_id_student]['ses_level'] == 0:
                d_school_stats_instance[s_school_id_newgoto]['students_low_ses'] += 1


            ### check rezoned
            if d_student['zoned_school'] != s_school_id_newzoned:
                i_rezoned_student_total += 1
                if config.d_cbs[s_cb_id_student]['ses_level'] == 0:
                    i_rezoned_student_lowses += 1


            ### travel time
            if np.isnan(self.d_car_time[s_cb_id_student][s_school_id_newgoto]):
                pass
            else:
                l_travel_time.append(self.d_car_time[s_cb_id_student][s_school_id_newgoto] / 60)


        ###
        d_student_stats_instance =  {
            "rezoned_student_lowses": i_rezoned_student_lowses,
            "rezoned_student_total": i_rezoned_student_total,
            "optout_student": i_optout_student,
            "travel_time_min": statistics.mean(l_travel_time)
        }


        return d_student_stats_instance, d_school_stats_instance

    def create_student_statistic_files(self, config, l_student_stats_instances):

        ### student statistics
        d_student_stats = {}
        for s_term in ["rezoned_student_lowses", "rezoned_student_total", "optout_student"]:

            l_values_term = [
                d_stat_instance[s_term]
                for d_stat_instance in l_student_stats_instances
            ]

            if s_term == "rezoned_student_lowses":
                i_denom = config.i_lowses_population
            else:
                i_denom = len(config.l_students)

            i_avg_pop = round(statistics.mean(l_values_term), 0)

            d_student_stats[s_term] = {
                "average": i_avg_pop,
                "percentage": round(i_avg_pop / i_denom * 100, 2),
                "values": l_values_term
            }

        for s_term in ['travel_time_min']:

            l_values_term = [
                d_stat_instance[s_term]
                for d_stat_instance in l_student_stats_instances
            ]

            d_student_stats[s_term] = {
                "average": round(statistics.mean(l_values_term), 2),
                "values": l_values_term
            }

        du.saveJson(
            d_student_stats,
            config.s_result_student_json_path
        )

    def create_school_statistic_files(self, config, l_school_stats_instances):


        d_school_stats_overall = {
            s_school_id: {"avg_zoned": 0, "avg_actual": 0, "lowses": [], "total": []}
            for s_school_id in config.l_school_ids
        }

        for s_school_id in config.l_school_ids:

            l_lowses_students = [
                d[s_school_id]['students_low_ses'] for d in l_school_stats_instances
            ]
            i_avg_lowses = round(statistics.mean(l_lowses_students), 0)

            l_total_students = [
                {
                    '#': d[s_school_id]['students_total'],
                    '+-%': round(
                        (d[s_school_id]['students_total'] - config.d_schools[s_school_id]['total_student_in_school'])
                        /
                        config.d_schools[s_school_id]['total_student_in_school'] * 100,
                        2
                    )
                }
                for d in l_school_stats_instances
            ]

            for d in l_total_students:
                assert(abs(d['+-%']) <= config.f_school_population_change_max_ratio * 100)

            i_avg_total = round(
                statistics.mean(
                    [d['#'] for d in l_total_students]
                ),
                0
            )


            d_school_stats_overall[s_school_id] = {}
            d_school_stats_overall[s_school_id] = {
                "avg_lowses": i_avg_lowses,
                "avg_total": i_avg_total,
                "lowses_percentage": round(i_avg_lowses / i_avg_total * 100, 2),
                "lowses": l_lowses_students,
                "total": l_total_students
            }

        du.saveJson(
            d_school_stats_overall,
            config.s_result_school_json_path
        )
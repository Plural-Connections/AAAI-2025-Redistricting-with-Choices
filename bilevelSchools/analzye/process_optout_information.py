import math

import geopandas as gpd

from bilevelSchools.analzye import draw_useful_maps
from bilevelSchools.utils import data_utils as du


def process(config):

    ### Initialize
    d_cb_count = {
        s_cb_id: 0
        for s_cb_id in config.l_cb_ids
    }

    d_students = {
        d_student['student_id']: d_student
        for d_student in config.l_students
    }

    d_optout_to_school = {
        i_school_id: 0
        for i_school_id in config.l_school_ids
    }

    ### CB results
    d_cb_results = du.loadJson(
        config.s_result_cb_json_path
    )

    ### Find who opt out
    for i_instance_idx in range(1, config.i_num_instances + 1):

        d_student_choices = du.loadJson(
            config.s_1_choice_instance_json_path.format(i_instance_idx)
        )

        for s_student_id in d_student_choices:

            s_cb_id = d_students[s_student_id]['census_block']

            s_school_id_zoned = d_cb_results[s_cb_id]['new_zoned_school']
            s_school_id_goto  = d_student_choices[s_student_id][s_school_id_zoned]

            if s_school_id_goto != s_school_id_zoned:
                d_cb_count[s_cb_id] += 1
                d_optout_to_school[s_school_id_goto] += 1

    ### average over instance
    d_cb_count = {
        s_cb_id: int(round(d_cb_count[s_cb_id] / config.i_num_instances, 0))
        for s_cb_id in config.l_cb_ids
    }
    d_optout_to_school = {
        s_school_id: int(round(d_optout_to_school[s_school_id] / config.i_num_instances, 0))
        for s_school_id in config.l_school_ids
    }

    du.saveJson(
        {
            "each_census_block": dict(
                sorted(
                    d_cb_count.items(),
                    key = lambda item: item[1],
                    reverse = True
                )
            ),
            "each_school_optout_in": dict(
                sorted(
                    d_optout_to_school.items(),
                    key = lambda item: item[1],
                    reverse = True
                )
            )
        },
        config.s_optout_count_json_path
    )


    ### ratio
    d_cb_ratio = {}
    for s_cb_id in config.l_cb_ids:
        if config.d_cbs[s_cb_id]['total_students_in_cb'] != 0:
            d_cb_ratio[s_cb_id] = round(
                d_cb_count[s_cb_id] / config.d_cbs[s_cb_id]['total_students_in_cb'], 2
            )
        else:
            d_cb_ratio[s_cb_id] = 0


    ### Load shapefiles
    df_cbs = gpd.read_file(
        config.s_census_block_shape_path
    )
    df_cbs['GEOID20'] = df_cbs['GEOID20'].astype(str)
    df_cbs = df_cbs.loc[
        df_cbs['GEOID20'].isin(config.l_cb_ids)
    ].reset_index()


    ### Map 1: Draw count map
    map_optout_count = draw_useful_maps.draw_student_opt_out_choropleth_map(
        config,
        df_cbs, d_cb_count,
        s_color_bar_title = "Number of Opt-out Students in Census Blocks",
        l_index = [1, 5, 10, 25, max(d_cb_count.values())]
    )
    map_optout_count.save(config.s_cb_optout_count_map_html_path)


    ### Map 2: Draw Ratio Map
    map_optout_ratio = draw_useful_maps.draw_student_opt_out_choropleth_map(
        config,
        df_cbs, d_cb_ratio,
        s_color_bar_title = "Ratio of Opt-out Students in Census Blocks"
    )
    map_optout_ratio.save(config.s_cb_optout_ratio_map_html_path)


    ### Map 3: Draw School Opt-out
    l_index_for_map = [
        0, 100, 200, 300,
        max(d_optout_to_school.values())
    ]
    map_school_opt_out = draw_useful_maps.draw_school_population(
        config, df_cbs,
        d_optout_to_school, d_cb_results, l_index_for_map,
        s_color_bar_title = 'Number of Opt-out students to each school'
    )
    map_school_opt_out.save(config.s_school_optout_count_map_html_path)



    ### Map 4: School population changes
    d_school_attendance_change = {}

    d_school_result = du.loadJson(
        config.s_result_school_json_path
    )

    for s_school_id in d_school_result.keys():
        d_school_attendance_change[s_school_id] = (
            int(d_school_result[s_school_id]['avg_total'])
            -
            config.d_schools[s_school_id]['total_student_in_school']
        )

    # one positive, one negative
    i_max_change = max(d_school_attendance_change.values())
    i_min_change = min(d_school_attendance_change.values())


    l_index_for_map = [
        i_min_change,
        math.floor(i_min_change / 2),
        0,
        math.floor(i_max_change / 2),
        i_max_change
    ]
    map_school_opt_out = draw_useful_maps.draw_school_population(
        config, df_cbs,
        d_school_attendance_change, d_cb_results, l_index_for_map,
        l_colors = [
            '#4B0082', '#D8BFD8', '#FFFF00', '#FFD700'
        ],
        s_color_bar_title = 'Changes of Attendances After Rezoning'
    )
    map_school_opt_out.save(config.s_school_attendance_change_map_html_path)
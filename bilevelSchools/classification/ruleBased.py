from bilevelSchools.classification import reporter
from bilevelSchools.utils import data_utils as du

import numpy as np

def run(config):

    d_time = du.loadJson(config.s_travel_time_json_path)

    run_1_time(config, d_time)

def run_1_time(config, d_time):

    ### Load everything from previous step
    a_y_pred_dist = [
        gen_1_distribution(config, d_time, d_student, d_student['zoned_school'])
        for d_student in config.l_students
    ]

    a_y_pred = np.array(
        [
            np.random.choice(len(row), size = 1, p = row)
            for row in a_y_pred_dist
        ]
    )

    ### Labels
    l_y_gt = du.loadJson(
        config.s_ml_labels_json_path
    )

    ### Report, still call it "fold" result although there is only 1 fold
    d_fold_result = reporter.evaluate_with_common_metrics(
        config, l_y_gt, a_y_pred, a_y_pred_dist, s_task_type = 'test'
    )
    d_fold_result_summary = reporter.result_averaged_over_folds([d_fold_result])

    reporter.produce_overall(
        config, l_y_gt, a_y_pred.tolist(), d_fold_result_summary
    )


def gen_1_distribution(config, d_time, d_student, s_school_id_zone):

    l_dist = [0] * len(config.l_schools)

    ### assign zoned school prob
    i_school_idx_zone = config.d_nces2idx[s_school_id_zone]
    l_dist[i_school_idx_zone] += 0.65

    ### magnet schools
    l_school_ids_magnet = [
        s_school_id
        for s_school_id in config.l_school_ids
        if 'Magnet' in config.d_schools[s_school_id]['Sub_Class']
    ]

    ### time
    d_travel_time_from_cb = d_time[d_student['census_block']]
    d_travel_time_from_cb_filtered = {
        k: v for k, v in d_travel_time_from_cb.items()
        if (not np.isnan(v)) and (k not in config.l_not_considred_kindergarten)
    }
    l_sorted_schools = sorted(
        d_travel_time_from_cb_filtered.items(),
        key = lambda x: x[1]
    )


    ### find top nearby school
    l_school_ids_nerby_12 = [l_sorted_schools[i][0] for i in range(12)]
    l_school_ids_nerby_5  = [l_sorted_schools[i][0] for i in range(5)]


    ### assign probs to magnet schools
    l_school_ids_nerby_magnet = list(
        set(l_school_ids_nerby_12).intersection(set(l_school_ids_magnet))
    )
    assert(len(l_school_ids_nerby_magnet) > 0)
    for s_school_id in l_school_ids_nerby_magnet:
        i_school_idx = config.d_nces2idx[s_school_id]
        l_dist[i_school_idx] += (
            0.2 / len(l_school_ids_nerby_magnet)
        )

    ### assign probls to nearby schools
    for s_school_id in l_school_ids_nerby_5:
        i_school_idx = config.d_nces2idx[s_school_id]
        l_dist[i_school_idx] += 0.03

    assert(abs(sum(l_dist) - 1) < 0.001)

    return l_dist
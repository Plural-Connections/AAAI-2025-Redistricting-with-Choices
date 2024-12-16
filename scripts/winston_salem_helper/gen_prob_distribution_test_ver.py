import sys
sys.path.append('../../')

import pandas as pd, numpy as np
import pyarrow # make pd stop complain for DeprecationWarning

from bilevelSchools.utils import data_utils as du


def get_dist_list(l_schools, s_school_id):


    # zone school probability
    f_zoned_val = np.random.uniform(0.667, 1)
    i_school_idx = l_schools.index(s_school_id)

    l_vals = np.random.rand(len(l_schools)).tolist()
    l_vals[i_school_idx] = f_zoned_val


    i_sum_random = sum(
        [
            l_vals[i]
            for i in range(len(l_vals))
            if i != i_school_idx
        ]
    )

    for i in range(len(l_vals)):

        if i == i_school_idx:
            continue

        l_vals[i] = l_vals[i] / i_sum_random * (1 - f_zoned_val)


    # adjust, make sure the sum is 1
    assert(
        abs(sum(l_vals) - 1) < 0.0001
    )

    l_vals = [round(x, 3) for x in l_vals]

    return l_vals


if __name__ == '__main__':

    # load data
    df_cb_school_relation = pd.read_csv(
        '../../data/with_ses_Elementary_blocks_to_schools_processed_data_wsfcs.csv'
    )

    l_schools = du.loadJson(
        '../../data/additional/list_of_schools.json'
    )

    d_prob_dist = {}
    for _, df_cb_row in df_cb_school_relation.iterrows():


        for i in range(1, int(df_cb_row['num_total_to_school']) + 1):

            s_id = '{}_{}'.format(df_cb_row['block_id'], str(i))
            d_prob_dist[s_id] = {
                'id': s_id,
                'cb': df_cb_row['block_id'],
                'all_distribution': []
            }

            for s_school_id in l_schools:

                d_prob_dist[s_id]['all_distribution'].append(
                    {
                        'zoned_school': s_school_id,
                        'zoned_school_idx': l_schools.index(s_school_id),
                        'distribution': get_dist_list(l_schools, s_school_id)
                    }
                )
        break
    du.saveJson(
        d_prob_dist,
        'student_to_school_distribution.json'
    )
import pandas as pd

from bilevelSchools.utils import data_utils as du


def parse(config, df_attendance):

    ### Load DF, filter out some rows
    df_attendance = df_attendance.loc[
        df_attendance['school_year'] == '2022-2023'
    ].reset_index()

    df_cb_ses_relation = pd.read_csv(
        config.s_census_block_ses_csv_path
    )
    df_cb_ses_relation['GEOID20'] = df_cb_ses_relation['GEOID20'].astype(str)

    ### get all appeared cbs
    set_all_cb_id = set(df_cb_ses_relation['GEOID20']).difference(set(config.l_not_considred_cbs))

    ### get all appeared races
    set_races = set(df_attendance['Race_Desc'])


    ### The CB Dict
    d_cb = {
        s_cb_id: {
            s_race: 0
            for s_race in set_races
        }
        for s_cb_id in set_all_cb_id
    }

    ### Total Race in The Study
    d_race = {
        s_race : 0
        for s_race in set_races
    }


    ### Start to iterate:
    for _, df_row in df_attendance.iterrows():

        s_cb_id = df_row['block_id']
        s_race = df_row['Race_Desc']
        d_cb[s_cb_id][s_race] += 1
        d_race[s_race] += 1


    i_num_total_student_in_study = sum(d_race.values())
    for s_cb_id in d_cb.keys():

        d_cb[s_cb_id]['total_students_in_cb'] = sum(d_cb[s_cb_id].values())
        if d_cb[s_cb_id]['total_students_in_cb'] == 0:
            continue

        d_cb[s_cb_id]['ratio_students_in_cb'] = (
            d_cb[s_cb_id]['total_students_in_cb']
            /
            i_num_total_student_in_study
        )

        for s_race in set_races:

            s_new_feat_name = 'ratio_{}_in_this_cb'.format(s_race)
            d_cb[s_cb_id][s_new_feat_name] = (
                d_cb[s_cb_id][s_race]
                /
                d_cb[s_cb_id]['total_students_in_cb']
            )

            s_new_feat_name = 'ratio_{}_this_cb_over_whole_study'.format(s_race)
            d_cb[s_cb_id][s_new_feat_name] = (
                d_cb[s_cb_id][s_race]
                /
                d_race[s_race]
            )


    d_cb = get_cb_and_ses(config, df_cb_ses_relation, d_cb)

    du.saveJson(
        d_cb,
        config.s_cb_features_json_path
    )

def get_cb_and_ses(config, df_cb_ses_relation, d_cb):

    for _, df_row in df_cb_ses_relation.iterrows():


        s_cb_id = str(df_row['GEOID20'])

        if int(df_row['GEOID20']) == 0:
            continue

        if str(df_row['GEOID20']) in config.l_not_considred_cbs:
            continue

        ### represent ses_level with 0, 1, and 2
        d_cb[s_cb_id]['ses_level'] = {
            'low': 0,
            'medium': 1,
            'high': 2
        }[df_row['ses_category_1_3']]

        d_cb[s_cb_id]['zoned_school'] = str(df_row['zoned_nces_id'])

    return d_cb
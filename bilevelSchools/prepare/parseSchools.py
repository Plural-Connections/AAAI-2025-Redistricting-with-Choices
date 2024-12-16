import pandas as pd, numpy as np

from bilevelSchools.utils import data_utils as du


# target: generate features_from_school.json
def parse(config, df_attendance):

    ########## School Attendance Info
    df_attendance_with_features = get_school_attendance_features(config, df_attendance)


    ############# Zone of Choice Info
    df_zone_of_choice = pd.read_csv(
        config.s_school_zone_of_choice_csv_path
    )[
        ['zoned_nces_id', 'zone_names']
    ].rename(
        columns = {
            'zoned_nces_id': 'nces_id',
            'zone_names': 'zone_of_choice_ids'
        }
    )
    df_zone_of_choice = df_zone_of_choice[df_zone_of_choice.nces_id != 0].drop_duplicates()
    df_zone_of_choice["nces_id"] = df_zone_of_choice["nces_id"].astype(str)
    df_zone_of_choice["zone_of_choice_ids"] = (
        df_zone_of_choice["zone_of_choice_ids"].astype(str).str.split(',')
    )


    ############# School Rating
    df_school_rate = pd.read_csv(
        config.s_school_rating_csv_path
    ).drop(
        columns = ['url', 'school_website', 'lat', 'long', 'school_name', 'gs_college_readiness_rating']
    )
    df_school_rate['nces_id'] = df_school_rate['nces_id'].astype(str)



    ########## School Programs
    df_school_program = pd.read_csv(
        config.s_school_program_csv_path
    ).drop(
        columns = [
            'Name', 'TITLE_I', 'SCHNUMBER', 'SCHZONE',	'School ID',

            # for elementary school, none of these have these entries
            'AVID',
            'Academy of Finance',
            'Academies of Hospitality& Tourism',
            'Construction, Pharmacy, Culinary',
            '6-12 Sports Mgmt and Human Services',

            # these info are not too important
            'Visual & Performing Arts',
            'Dual Language Immersion (Spanish)',
            'STEM/STEAM',
            'International Baccalaureate (IB) / Dual Language Immersion',
            'Fire Academy',
            "Intern'l Studies/Dual Lang (Two-Way Chinese)",
            "Dual Lang (One-Way Spanish)"
        ]
    ).fillna(0)
    df_school_program = df_school_program[df_school_program.nces_id.notnull()]
    df_school_program = df_school_program[df_school_program['SCH_TYPE'] == 'Elementary']
    df_school_program['nces_id'] = df_school_program['nces_id'].astype(int).astype(str)


    ### Merge and Save
    df_school = df_attendance_with_features.merge(
        df_school_rate,
        on = "nces_id"
    ).merge(
        df_zone_of_choice,
        on = "nces_id"
    ).merge(
        df_school_program,
        on = "nces_id"
    ).replace(np.nan, None)

    d_school = df_school.sort_values(
        by = ['nces_id']
    ).set_index(
        'nces_id', drop = False
    ).to_dict('index')


    du.saveJson(
        d_school,
        config.s_school_features_json_path
    )


def get_school_attendance_features(config, df_attendance):


    ### Load DF
    df_attendance = df_attendance.loc[
        df_attendance['school_year'] == '2022-2023'
    ].reset_index()
    set_all_school_id = set(df_attendance['nces_id'])


    ### The studnets who actually go to these schools
    d_school_actual_feat = {

        s_school_id: {
            s_race: 0
            for s_race in config.l_races
        }
        for s_school_id in set_all_school_id

    }


    ### Total Race in The Study
    d_race = {
        s_race : 0
        for s_race in config.l_races
    }

    ### Start to iterate:
    for _, df_row in df_attendance.iterrows():

        s_actual_school_id = df_row['nces_id']
        s_race             = df_row['Race_Desc']

        d_school_actual_feat[s_actual_school_id][s_race] += 1
        d_race[s_race] += 1


    ###
    i_num_total_student_in_study = sum(d_race.values())

    l_attend_features = []
    for s_school_id in set_all_school_id:

        d_school = d_school_actual_feat[s_school_id]

        d_school['total_student_in_school'] = sum(d_school.values())

        d_school['nces_id'] = s_school_id

        # d_school['ratio_student_in_study'] = (
        #     d_school['total_student_in_school']
        #     /
        #     i_num_total_student_in_study
        # )


        # for s_race in config.l_races:

        #     s_new_feat_name = 'ratio_{}_in_this_school'.format(s_race)
        #     d_school[s_new_feat_name] = (
        #         d_school[s_race]
        #         /
        #         d_school['total_student_in_school']
        #     )

        #     s_new_feat_name = 'ratio_{}_this_school_over_whole_study'.format(s_race)
        #     d_school[s_new_feat_name] = (
        #         d_school[s_race]
        #         /
        #         d_race[s_race]
        #     )

        l_attend_features.append(d_school)

    return pd.DataFrame(l_attend_features)
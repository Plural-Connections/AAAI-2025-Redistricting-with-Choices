import ast

from bilevelSchools.utils import data_utils as du

def parse(config, df_attendance):


    ### Figure out the student's attendance from previous years
    df_student_record_before_target = df_attendance.loc[~df_attendance['school_year'].isin(['2022-2023', '2023-2024'])].reset_index()
    d_record_previous_years = get_attendance_records(config, df_student_record_before_target)

    l_attendance_previous_years_break_down = [
        get_attendance_records(
            config,
            df_attendance.loc[df_attendance['school_year'] == "2019-2020"].reset_index()
        ),
        get_attendance_records(
            config,
            df_attendance.loc[df_attendance['school_year'] == "2020-2021"].reset_index()
        ),
        get_attendance_records(
            config,
            df_attendance.loc[df_attendance['school_year'] == "2021-2022"].reset_index()
        )
    ]

    ### start to parse 2022-2023
    df_students_target_year = df_attendance.loc[df_attendance['school_year'] == "2022-2023"].reset_index()
    d_record_target_year = get_attendance_records(config, df_students_target_year)

    ### need census block data to DOUBLE CHECK zoned information
    d_cb = du.loadJson(config.s_cb_features_json_path)


    l_students = []
    for _, df_row in df_students_target_year.iterrows():

        d_student_target_year = get_student_info_on_target_year(df_row, d_cb)

        d_student_target_year = add_multiple_schools_feature(
            d_record_previous_years, d_student_target_year
        )

        d_student_target_year = add_siblings_feature(
            l_attendance_previous_years_break_down,
            d_record_target_year['attedance_check_dict'], # this contains all students in that year
            d_student_target_year, # this only deal with 1 student we are processing
        )

        l_students.append(d_student_target_year)

        ### Clean
        del d_student_target_year['siblings']


    ### get some statistics
    i_total_go_to_zoned = sum(
        [
            bool(d['zoned_school'] == d['actual_school'])
            for d in l_students
        ]
    )
    print(i_total_go_to_zoned, len(l_students))

    l_students = sorted(l_students, key = lambda d: d['student_id'])

    du.saveJson(
        l_students,
        config.s_student_features_json_path
    )

def get_student_info_on_target_year(df_row, d_cb):

    assert(
        df_row['zoned_nces_id'] == d_cb[str(df_row['block_id'])]['zoned_school']
    )

    if "," in df_row['sibling_IDs']:
        l_siblings = ast.literal_eval(df_row['sibling_IDs'])
    else:
        l_siblings = [ast.literal_eval(df_row['sibling_IDs'])]

    return {
        "student_id": df_row['ID'],
        'race': df_row['Race_Desc'],
        "zoned_school": df_row['zoned_nces_id'],
        "actual_school": df_row['nces_id'],
        "census_block": df_row['block_id'],
        "siblings": [str(x) for x in l_siblings],
        "grade": df_row['GRADE_LEVEL'],
    }


def get_attendance_records(config, df_student_record):

    ### df_student_record can contain 1 year data or multiple years data

    d_attendance = {}
    d_opt_out    = {}
    for _, df_row in df_student_record.iterrows():

        if df_row['ID'] not in d_attendance.keys():

            d_attendance[df_row['ID']] = set(
                [df_row['nces_id']]
            )

            d_opt_out[df_row['ID']] = {}
            d_opt_out[df_row['ID']]['has_opt_out'] = int(
                df_row['zoned_nces_id'] != df_row['nces_id']
            )

            d_opt_out[df_row['ID']]['has_opt_out_to_magnet'] = int(
                bool(df_row['zoned_nces_id'] != df_row['nces_id'])
                and
                bool('Magnet' in config.d_schools[df_row['nces_id']]['Sub_Class'])
            )

        else:
            d_attendance[df_row['ID']].add(
                df_row['nces_id']
            )

            d_opt_out[df_row['ID']]['has_opt_out'] = int(
                bool(d_opt_out[df_row['ID']]['has_opt_out'])
                or
                (df_row['zoned_nces_id'] != df_row['nces_id'])
            )

            d_opt_out[df_row['ID']]['has_opt_out_to_magnet'] = int(
                d_opt_out[df_row['ID']]['has_opt_out_to_magnet']
                or
                (
                    bool(df_row['zoned_nces_id'] != df_row['nces_id'])
                    and
                    bool('Magnet' in config.d_schools[df_row['nces_id']]['Sub_Class'])
                )
            )

    ### Basic Stats
    i_num_students_go_to_more_1_school = 0
    set_appeared_schools = set()
    for s_id in d_attendance.keys():

        if len(d_attendance[s_id]) > 1:
            i_num_students_go_to_more_1_school += 1

        set_appeared_schools = set_appeared_schools.union(
            d_attendance[s_id]
        )
    print('{} students have attended more than 1 school'.format(i_num_students_go_to_more_1_school))
    print('{} schools appeared'.format(len(set_appeared_schools)))

    return {
        "attedance_check_dict": d_attendance,
        "opt_out_check_dict": d_opt_out
    }

def add_siblings_feature(l_attendance_previous_years_break_down, d_attendance_target_year, d_student):

    ### Figure out relation with siblings' schools
    d_student['went_to_same_school_with_sibling'] = 0
    d_student['has_elementary_siblings'] = 0
    s_student_id = d_student['student_id']
    l_siblings   = d_student['siblings']


    ### Figure out if student has sibling going to elementary school this year
    for s_sibling_id in l_siblings:
        if s_sibling_id in d_attendance_target_year.keys():
            d_student['has_elementary_siblings'] = 1


    for d_record_that_year in l_attendance_previous_years_break_down:
        d_attendance_that_year = d_record_that_year['attedance_check_dict']

        for s_sibling_id in l_siblings:

            ### both the student and their sibling are in elmentary school in that year (could be 19-20, 20-21, or 21-22)
            if (
                (s_student_id in d_attendance_that_year.keys())
                and
                (s_sibling_id in d_attendance_that_year.keys())
            ):

                if d_attendance_that_year[s_student_id] == d_attendance_that_year[s_sibling_id]:
                    d_student['went_to_same_school_with_sibling'] = 1
                    return d_student


    return d_student


def add_multiple_schools_feature(d_record_previous_years, d_student):

    ### Figure out relation with previous years attendance
    if d_student['student_id'] in d_record_previous_years['attedance_check_dict'].keys():
        d_student['previous_schools'] = list(
            d_record_previous_years['attedance_check_dict'][d_student['student_id']]
        )
        d_student['has_opt_out_before']           = d_record_previous_years['opt_out_check_dict'][d_student['student_id']]['has_opt_out']
        d_student['has_opt_out_to_magnet_before'] = d_record_previous_years['opt_out_check_dict'][d_student['student_id']]['has_opt_out_to_magnet']
    else:
        d_student['previous_schools']             = list()
        d_student['has_opt_out_before']           = 0
        d_student['has_opt_out_to_magnet_before'] = 0

    d_student['newly_joined_student'] = int(
        len(d_student['previous_schools']) == 0
    )
    d_student['went_to_multiple_schools_before'] = int(
        len(d_student['previous_schools']) > 1
    )

    return d_student

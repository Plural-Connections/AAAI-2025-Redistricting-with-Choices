from bilevelSchools.prepare import (
    parseCensusBlock,
    parseCensusBlockNeighbor,
    parseSchools,
    parseStudents
)

import pandas as pd


def run_prepare_pipeline(config):


    df_attendance = pd.read_csv(
        config.s_student_raw_info_csv_path
    )

    ### Change Values
    df_attendance['ID'] = df_attendance['ID'].astype(str)
    df_attendance['zoned_nces_id'] = df_attendance['zoned_nces_id'].astype(str)
    df_attendance['nces_id'] = df_attendance['nces_id'].astype(str)
    df_attendance['block_id'] = df_attendance['block_id'].astype(str)
    df_attendance['Race_Desc'] = df_attendance['Race_Desc'].map(config.d_race_name_map)

    ### Drop some not relevant schools
    df_attendance = df_attendance[~df_attendance['nces_id'].isin(config.l_not_considred_kindergarten)]


    ### get "features_from_census_blocks.json"
    parseCensusBlock.parse(config, df_attendance)

    ### get "features_from_schools.json"
    parseSchools.parse(config, df_attendance)

    ### get "features_from_students.json"
    config._load_school_data()
    parseStudents.parse(config, df_attendance)

    ### get "census_blocks_and_neighbors.json"
    config._load_key_data()
    parseCensusBlockNeighbor.parse(config)
import pandas as pd, geopandas as gpd
import folium

from bilevelSchools.utils import data_utils as du

def visualize(config, d_school_assignment = None):

    map_asg = folium.Map(
        config.l_center_coord,
        tiles = 'cartodbpositron'
    )

    ### Visualize Schools
    visualize_school(config, map_asg)

    ### Visualize Assignment
    if d_school_assignment == None:
        ### in this case, d_school_assignment is not treated as input, so we load
        # cb ---> school idx (not school id)
        d_school_assignment = get_school_assignment_from_result(config)
    else:
        pass
    visualize_assignment(config, map_asg, d_school_assignment)

    map_asg.save(
        config.s_school_assignment_html_path
    )

def visualize_school(config, map_asg):


    ### load the school rating file here because it has the lat lon info
    # some school nces id is not a digit, cannot be converted to an int later
    df_school_details = pd.read_csv(
        config.s_school_rating_csv_path
    )

    df_school_details = df_school_details.loc[
        df_school_details['nces_id'].isin(config.l_school_ids)
    ]

    for _, df_row in df_school_details.iterrows():

        folium.Marker(
            [
                df_row['lat'], df_row['long']
            ],
            tooltip = df_row['nces_id'],
            icon = folium.features.CustomIcon(
                config.s_school_icon_url,
                icon_size = (10, 10),

            )
        ).add_to(map_asg)


def get_school_assignment_from_result(config):

    d_cb_result = du.loadJson(
        config.s_result_cb_json_path
    )

    return {
        int(i_cb_id): d_cb_result[i_cb_id]['new_zoned_school']
        for i_cb_id in d_cb_result.keys()
    }


def visualize_assignment(config, map_asg, d_school_assignment):


    ### Load shapefiles
    df_cb_shapes = gpd.read_file(
        config.s_census_block_shape_path
    )
    df_cb_shapes['GEOID20'] = df_cb_shapes['GEOID20'].astype(str)
    df_cb_shapes = df_cb_shapes.loc[
        df_cb_shapes['GEOID20'].isin(config.l_cb_ids)
    ]

    ### Load School Color on Map
    d_school_colors = du.loadJson(
        config.s_school_map_color_json_path
    )

    for s_school_id in config.l_school_ids:

        l_cb_to_sch = [
            s_cb_id
            for s_cb_id in d_school_assignment.keys()
            if d_school_assignment[s_cb_id] == config.d_nces2idx[s_school_id]
        ]

        df_cb_school = df_cb_shapes.loc[
            df_cb_shapes['GEOID20'].isin(l_cb_to_sch)
        ]

        s_color_code = d_school_colors[str(s_school_id)]

        folium.GeoJson(
            data = df_cb_school['geometry'],
            style_function = lambda feature, fillColor = s_color_code: {
                'fillColor': fillColor,
                'fillOpacity': 1,

                # these two lines are needed to overwrite the default blue boundaries
                'color': 'black',
                'weight': 0.0
            }
        ).add_to(
            map_asg
        )


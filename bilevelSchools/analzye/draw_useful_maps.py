import folium
import branca.colormap as cm, numpy as np

def draw_student_opt_out_choropleth_map(config, df_cbs, d_input, s_color_bar_title = '', l_index = None):

    map_optout = folium.Map(
        config.l_center_coord,
        tiles = 'cartodbpositron'
    )

    l_values_greater_than_0 = [
        x
        for x in d_input.values()
        if x > 0
    ]

    if l_index == None:
        l_index = [
            min(l_values_greater_than_0),
            np.percentile(l_values_greater_than_0, 25),
            np.percentile(l_values_greater_than_0, 50),
            np.percentile(l_values_greater_than_0, 75),
            max(l_values_greater_than_0)
        ]

    color_step = cm.StepColormap(
        ["#abced8", "#2ca9e1", "#1e50a2", "#010048"],
        vmin = min(l_values_greater_than_0),
        vmax = max(l_values_greater_than_0),
        index = l_index,
        caption = s_color_bar_title
    )


    ### apply a for loop here because it is easier to debug
    for i_idx, df_cb_row in df_cbs.iterrows():

        if d_input[df_cb_row['GEOID20']] == 0:
            continue
        else:
            s_color_code = color_step(d_input[df_cb_row['GEOID20']])

        folium.GeoJson(
            data = df_cb_row['geometry'],
            style_function = lambda feature, fillColor = s_color_code: {
                'fillColor': fillColor,

                'fillOpacity': 1,

                # these two lines are needed to overwrite the default blue boundaries
                'color': 'black',
                'weight': 0
            }
        ).add_to(
            map_optout
        )

    color_step.add_to(map_optout)

    return map_optout


def draw_school_population(
        config, df_cbs, d_input, d_cb_result,
        l_index,
        l_colors = ["#abced8", "#2ca9e1", "#1e50a2", "#010048"],
        s_color_bar_title = ''
):

    map_optout = folium.Map(
        config.l_center_coord,
        tiles = 'cartodbpositron'
    )

    color_step = cm.StepColormap(
        l_colors,
        vmin = l_index[0],
        vmax = l_index[-1],
        index = l_index,
        caption = s_color_bar_title
    )


    ### apply a for loop here because it is easier to debug
    for i_idx, df_cb_row in df_cbs.iterrows():

        i_school_id_new_zoned = d_cb_result[df_cb_row['GEOID20']]['new_zoned_school']

        s_color_code = color_step(
            d_input[i_school_id_new_zoned]
        )

        folium.GeoJson(
            data = df_cb_row['geometry'],
            style_function = lambda feature, fillColor = s_color_code: {
                'fillColor': fillColor,

                'fillOpacity': 1,

                # these two lines are needed to overwrite the default blue boundaries
                'color': 'black',
                'weight': 0
            }
        ).add_to(
            map_optout
        )

    color_step.add_to(map_optout)

    return map_optout
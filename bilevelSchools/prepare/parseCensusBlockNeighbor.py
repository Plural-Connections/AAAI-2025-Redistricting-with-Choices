from networkx.readwrite import json_graph

from bilevelSchools.utils import data_utils as du


def parse(config):

    d_school_cb = du.loadJson(
        config.s_cb_school_network_json_path
    )

    # now query each necs id will give us a graph
    d_school_cb_nx = prep_blocks_networks(d_school_cb)

    distill_network_info_for_blocks(config, d_school_cb_nx)


def prep_blocks_networks(d_school_cb):
    for s_school_id in d_school_cb:
        d_school_cb[s_school_id] = json_graph.node_link_graph(
            d_school_cb[s_school_id]
        )
    return d_school_cb


def distill_network_info_for_blocks(config, d_school_cb_nx):
    d_cb_neighbors = {}

    for s_school_id in d_school_cb_nx:

        l_cbs_zoned_to_this_school = [
            s_cb_id
            for s_cb_id in config.l_cb_ids
            if config.d_cbs[s_cb_id]['zoned_school'] == s_school_id
        ]

        graph_school = d_school_cb_nx[s_school_id]
        l_nodes = graph_school.nodes(data = True)

        for s_cb_id in l_cbs_zoned_to_this_school:


            # If the block is not in the graph, skip it
            if not int(s_cb_id) in graph_school:
                continue

            # Get only the neighbors that are also zoned for the same school as the block
            neighbor_blocks = graph_school.neighbors(int(s_cb_id))

            # filter by ones that are in the df
            neighbor_blocks = filter(lambda x: str(x) in l_cbs_zoned_to_this_school, neighbor_blocks)

            l_neighbors_to_save = list(
                filter(
                    lambda x: l_nodes[x]["attrs"]["orig_school_id"] == int(s_school_id),
                    neighbor_blocks,
                )
            )

            d_cb_neighbors[s_cb_id] = [str(x) for x in l_neighbors_to_save]


    du.saveJson(
        d_cb_neighbors,
        config.s_cb_neighbor_json_path
    )
from bilevelSchools.classification import reporter
from bilevelSchools.utils import data_utils as du

def run(config):

    ### Load everything from previous step
    l_y_assumed_go_zoned = [
        config.d_nces2idx[d_student['zoned_school']]
        for d_student in config.l_students
    ]

    ### Labels
    l_y_gt = du.loadJson(
        config.s_ml_labels_json_path
    )

    ### Report
    reporter.produce_overall(
        config, l_y_gt, l_y_assumed_go_zoned
    )
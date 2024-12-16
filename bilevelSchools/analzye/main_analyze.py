
from bilevelSchools.analzye import (
    process_optout_information,
    report_optout_stats
)

def run_analyze_pipeline(config):


    ###
    process_optout_information.process(config)
    report_optout_stats.report(config)
from bilevelSchools.rezone import evaluate_solution, model_cp_with_choices, visualize_assignment

def run_rezone_pipeline(config):

    ### Before solving
    evaluator = evaluate_solution.solutionEvaluator(config)
    if config.b_only_evaluate_current_case:
        # get the very basic benchmark, which is the current districting (made by expert people)
        d_school_assignment = evaluator._evaluate_current(config)
    else:

        if config.b_directly_load_rezone_result:
            print('Not optimizing anything here, only evaluating the results')

            ### directly get assignment
            d_school_assignment = evaluator.load_saved_assignment(config)

        else:

            ### Construct Model
            model = model_cp_with_choices.OptimizationModel(config)

            ### solve model get assignment
            d_school_assignment = model.solve(config, evaluator)


    ### Report statistics and visualization
    evaluator.report_results(config, d_school_assignment)
    visualize_assignment.visualize(config, d_school_assignment)
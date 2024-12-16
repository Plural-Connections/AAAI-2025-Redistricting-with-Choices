import statistics, json, os



if __name__ == '__main__':

    s_method  = 'ml'
    l_results = []
    i = 0

    # Open the file in read mode
    with open('pars_rezone_stable_test.txt', 'r') as file:

        for s_line in file:

            if s_method not in s_line.split(' ')[3]:
                continue

            i_random_seed = s_line.split(' ')[5]

            l_json_files = [

                'scratch/bilevel_school_{}_stable_test_{}/optimization_{}_with_choices_{}/results_cp_summary_after_{}.0_hours.json'.format(

                    # folder 1
                    s_method,
                    s_end,

                    # folder 2
                    s_method,
                    i_random_seed,

                    i_hour
                )
                for s_end, i_hour in [
                    ['50_instances_4_hours',  4],
                    ['50_instances_6_hours',  6],
                    ['50_instances_8_hours',  8],
                    ['50_instances_12_hours', 12]
                ]
            ]

            l_seed_result = []
            for s_json_file_name in l_json_files:
                s_json_path = os.path.join(
                    os.environ.get('HOME'),
                    s_json_file_name
                )
                with open(s_json_path, 'r') as json_file:
                    d_1_res = json.load(json_file)
                    f_score = d_1_res['obj_evaluator'][1]
                l_seed_result.append(f_score)


            if min(l_seed_result) < 0.47:
                i += 1
            else:
                print('{} does not provide desired results'.format(i_random_seed))

            l_results.append(min(l_seed_result))

    print(sorted(l_results))
    print('{} below 0.47'.format(i))
    print('mean: {}'.format(statistics.mean(l_results)))
    print('stdev: {}'.format(statistics.stdev(l_results)))
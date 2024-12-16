# All .slurm files are ignored because of account information

# Prepare Key Data for the whole study, probably only needs to run it once, it parse the raw data into certain formats
 - Same thing for all methods
     ```
     python prepare_main.py
     ```

# Choice Modeling

 - choice model = follow, optimization model = cp with choices
    ```
    python classify_main.py --s_input_dir_par_yaml_path ./experiments/aaai2025/pars_follow_with_choices.yaml
    ```
 - choice model = rule-based, optimization model = cp with choices
    ```
    python classify_main.py --s_input_dir_par_yaml_path ./experiments/aaai2025/pars_rb_with_choices.yaml
    ```
 - choice model = machine learning (logit), optimization model = cp with choices
    ```
    python classify_main.py --s_input_dir_par_yaml_path ./experiments/aaai2025/pars_ml_with_choices_logit.yaml
    ```
 - choice model = machine learning (xgboost), optimization model = cp with choices
    ```
    python classify_main.py --s_input_dir_par_yaml_path ./experiments/aaai2025/pars_ml_with_choices_xgboost.yaml
    ```


# Generate Instances
 - choice model - current (using realistic data):
    ```
    python gen_instances_main.py --s_input_dir_par_yaml_path ./experiments/aaai2025/pars_current.yaml
    ```

 - choice model - follow:
    ```
    python gen_instances_main.py --s_input_dir_par_yaml_path ./experiments/aaai2025/pars_follow_with_choices.yaml
    ```

 - choice model - rule-based (use cluster, each instance takes a few mintues)
    ```
    python gen_instances_main.py --s_input_dir_par_yaml_path ./experiments/aaai2025/pars_rb_with_choices.yaml
    ```

 - choice model - machine learning (use cluster)

    Step 1: Train Model
    use `train_full_ml_model.slurm` at this step

    ```
    python gen_instances_main.py --s_input_dir_par_yaml_path ./experiments/aaai2025/pars_ml_with_choices_xgboost.yaml --b_train_a_new_model_to_generate_instance True
    ```

    Step 2: Generate Instances (each instance takes about 3-5 hours)
    ```
    python gen_instances_in_parallel.py --s_input_dir_par_yaml_path ./experiments/aaai2025/pars_ml_with_choices_xgboost.yaml --i_instance_idx 1
    ```


# Rezone Optimization (use cluster)
 - without choice model, do not optimize, use realistic data
    ```
    python rezone_main.py --s_input_dir_par_yaml_path ./experiments/aaai2025/pars_current.yaml
    ```

 - choice model = follow, optimization model = R
    ```
    python rezone_main.py --s_input_dir_par_yaml_path ./experiments/aaai2025/pars_follow_with_choices.yaml
    ```
 - choice model = rule-based, optimization model = FR
    ```
    python rezone_main.py --s_input_dir_par_yaml_path ./experiments/aaai2025/pars_rb_with_choices_xgboost.yaml
    ```
 - choice model = machine learning, optimization model = RWC
    ```
    python rezone_main.py --s_input_dir_par_yaml_path ./experiments/aaai2025/pars_ml_with_choices_xgboost.yaml
    ```

# Rezone Optimization SAA Test (use cluster)
- check 'pars_rezone_stable_test.txt'
one example:
    ```
    python rezone_main.py --s_input_dir_par_yaml_path ./experiments/aaai2025/pars_ml_with_choices_xgboost.yaml --s_optimization_result_dir scratch/bilevel_school_ml_stable_test_50_instances_12_hours/optimization_ml_with_choices_68444 --i_random_seed_for_picking_instances 68444 --i_cp_max_solving_hour 12
    ```
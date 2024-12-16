import statistics

from sklearn.metrics import (
    accuracy_score, top_k_accuracy_score,
    confusion_matrix, ConfusionMatrixDisplay, classification_report
)
import matplotlib.pyplot as plt

from bilevelSchools.utils import data_utils as du

def evaluate_with_common_metrics(
    config, l_y_gt, l_y_compare, l_y_compare_dist, s_task_type = 'test'
):

    f_acc_regular = accuracy_score(l_y_gt, l_y_compare)
    f_acc_top_3   = top_k_accuracy_score(l_y_gt, l_y_compare_dist, k = 3)
    f_acc_top_5   = top_k_accuracy_score(l_y_gt, l_y_compare_dist, k = 5)

    a_cm = confusion_matrix(
        l_y_gt,
        l_y_compare,
        labels = list(config.d_idx2nces.keys())
    )

    du.print_key_msg()
    print('The set we are reporting {}'.format(s_task_type))
    print('Regular Accuracy: {}'.format(f_acc_regular))
    print('Top 3 Accuracy: {}'.format(f_acc_top_3))
    print('Top 5 Accuracy: {}'.format(f_acc_top_5))
    print(a_cm)

    d_fold_result = {
        "acc": f_acc_regular,
        "top_3_acc": f_acc_top_3,
        "top_5_acc": f_acc_top_5
    }
    return d_fold_result

def result_averaged_over_folds(l_fold_res):
    d_avg_result = {
        "avg_over_folds: {}".format(
            s_fold_metric
        ): statistics.mean(
            [
                d_fold_res[s_fold_metric]
                for d_fold_res in l_fold_res
            ]
        )
        for s_fold_metric in [
            'acc', 'top_3_acc', 'top_5_acc'
        ]
    }

    d_list_result = {
        s_fold_metric: (
            [
                d_fold_res[s_fold_metric]
                for d_fold_res in l_fold_res
            ]
        )
        for s_fold_metric in [
            'acc', 'top_3_acc', 'top_5_acc'
        ]
    }

    return {
        **d_avg_result,
        **d_list_result
    }


def produce_overall(config, l_y_gt, l_y_compare, d_avg_fold_results = None):

    a_cm = confusion_matrix(
        l_y_gt,
        l_y_compare,
        labels = list(config.d_idx2nces.keys())
    )

    image_cm = ConfusionMatrixDisplay(
        confusion_matrix = a_cm,
        display_labels = list(set(l_y_gt))
    )


    ### Plot the confusion matrix
    _, ax = plt.subplots(figsize=(16, 14))  # Adjust the size as needed
    image_cm.plot(ax = ax, cmap = plt.cm.Blues)

    # Add a title and adjust layout if desired
    plt.title('Confusion Matrix')
    plt.tight_layout()


    # Save the plot as a PNG file
    plt.savefig(
        config.s_overall_confusion_matrix_png_path
    )

    ### gen the report with sklearn learn
    d_report = classification_report(
        l_y_gt, l_y_compare,
        output_dict = True
    )

    if d_avg_fold_results == None:
        pass
    else:
        d_report = {
            **d_report,
            **d_avg_fold_results
        }

    du.saveJson(
        d_report,
        config.s_key_matrices_report_json_path
    )
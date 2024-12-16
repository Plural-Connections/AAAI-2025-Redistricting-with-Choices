import sys
sys.path.append('../../')

from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix

from bilevelSchools.configuration import configuration

import matplotlib.pyplot as plt

# --s_input_dir_par_yaml_path place_holder.yaml
if __name__ == '__main__':

    config = configuration.Config()
    config._load_key_data()

    l_zoned = [
        config.d_nces2idx[d['zoned_school']]
        for d in config.l_students
    ]

    l_goto = [
        config.d_nces2idx[d['actual_school']]
        for d in config.l_students
    ]

    a_cm = confusion_matrix(
        l_zoned,
        l_goto,
        labels = list(config.d_idx2nces.keys())
    )

    image_cm = ConfusionMatrixDisplay(
        confusion_matrix = a_cm,
        display_labels = list(set(l_zoned))
    )


    ### Plot the confusion matrix
    _, ax = plt.subplots(figsize=(16, 14))  # Adjust the size as needed
    image_cm.plot(ax = ax, cmap = plt.cm.Blues)

    # Add a title and adjust layout if desired
    plt.title('Population of Schools in the Dataset')
    plt.tight_layout()

    plt.xlabel('Actual School')
    plt.ylabel('Zoned School')

    # Save the plot as a PNG file
    plt.savefig(
        'population_each_school_in_data.png'
    )
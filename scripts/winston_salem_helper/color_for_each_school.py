import sys
sys.path.append('../../')

import random

from bilevelSchools.utils import data_utils as du


if __name__ == '__main__':

    l_schools = du.loadJson(
        '../../data/additional/list_of_schools.json'
    )

    d_school_colors = {
        i_school_id: '#{:06x}'.format(
            random.randint(0, 0xFFFFFF)
        )
        for i_school_id in l_schools
    }

    du.saveJson(d_school_colors, 'school_colors_on_map.json')
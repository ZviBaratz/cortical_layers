import os

import numpy as np

from brain_matrix import BrainMatrix
from cfg import results_dir, n_classes


class SummaryResults:
    def __init__(self):
        """
        Class to help access summary results as a results set
        """
        self.path = os.path.join(results_dir, 'summary')

    def get_mean_probability_map_path(self, class_idx: int, atlas_name: str = 'AAL') -> str:
        """
        Returns the expected path for an existing 3D class mean probability map

        :param class_idx: class index
        :type class_idx: int
        :param atlas_name: name of the atlas used as template
        :type atlas_name: str
        :return: path to npy file
        :rtype: str
        """
        return os.path.join(self.path, 'mean', f'class_{class_idx}_{atlas_name}.npy')

    def get_mean_probability_map(self, class_idx: int, atlas_name: str = 'AAL') -> np.ndarray:
        """
        Returns the 3D probability map for the chosen class over the chosen atlas as template

        :param class_idx: class index
        :type class_idx: int
        :param atlas_name: name of the atlas used as template
        :type atlas_name: str
        :return: class mean probability map across subjects
        :rtype: np.ndarray
        """
        path = self.get_mean_probability_map_path(class_idx, atlas_name)
        return np.load(path)

    def get_mean_brain_matrix(self, class_idx: int, atlas_name: str = 'AAL') -> BrainMatrix:
        """
        Create a BrainMatrix instance with the mean class probability map

        :param class_idx: class index
        :type class_idx: int
        :param atlas_name: name of the atlas used as template
        :type atlas_name: str
        :return: probability map as BrainMatrix instance
        :rtype: BrainMatrix
        """
        probability_map = self.get_mean_probability_map(class_idx, atlas_name)
        info_dict = info={'subject': 'mean', 'class': class_idx}
        return BrainMatrix(probability_map, info_dict)

    def get_all_class_means(self, atlas_name: str = 'AAL'):
        """
        Returns a list of BrainMatrix instances for each class mean probability map

        :param atlas_name: name of the atlas used as template
        :type atlas_name: str
        :return: all class mean probability maps
        :rtype: list of BrainMatrix instances
        """
        return [self.get_mean_brain_matrix(class_idx, atlas_name) for class_idx in range(n_classes)]

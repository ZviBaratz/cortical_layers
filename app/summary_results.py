import os

import numpy as np

from brain_matrix import BrainMatrix
from cfg import raw_data_dir, results_dir, n_classes


class SummaryResults:
    def __init__(self):
        """
        Class to help access summary results as a results set
        """
        self.path = os.path.join(results_dir, 'summary')
        self.mean_dir = os.path.join(self.path, 'mean')
        self.mean_pbr_path = os.path.join(self.mean_dir, 'mean_pbr_matrix.npy')
        if self.has_summary('mean'):
            self.mean_pbr = np.load(self.mean_pbr_path)

    def has_summary(self, kind: str = 'mean'):
        return os.path.isfile(self.mean_pbr_path)

    def has_probability_maps(self, kind: str = 'mean'):
        return all([os.path.isfile(pmap_path) for pmap_path in self.get_all_mean_probability_map_paths()])

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
        return os.path.join(self.mean_dir, f'class_{class_idx}_{atlas_name}.npy')

    def get_all_mean_probability_map_paths(self, atlas_name: str = 'AAL'):
        return [self.get_mean_probability_map_path(class_idx, atlas_name) for class_idx in range(n_classes)]

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
        if os.path.isfile(path):
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
        if isinstance(probability_map, np.ndarray):
            info_dict = info = {'subject': 'mean', 'class': class_idx}
            return BrainMatrix(probability_map, info_dict)

    def get_all_class_means(self, atlas_name: str = 'AAL'):
        """
        Returns a list of BrainMatrix instances for each class mean probability map

        :param atlas_name: name of the atlas used as template
        :type atlas_name: str
        :return: all class mean probability maps
        :rtype: list of BrainMatrix instances
        """
        if self.has_probability_maps('means'):
            return [self.get_mean_brain_matrix(class_idx, atlas_name) for class_idx in range(n_classes)]

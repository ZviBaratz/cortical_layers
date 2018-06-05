import os

import numpy as np

from brain_matrix import BrainMatrix
from cfg import results_dir, n_classes


class Subject:
    def __init__(self, subject_id: str, pbr: np.ndarray):
        """
        General subject class for the app to easily associate data

        :param subject_id: subject unique identifier
        :type subject_id: str
        :param pbr: class probability by region matrix
        :type pbr: np.ndarray
        """
        self.subject_id = subject_id
        self.results_dir = os.path.join(results_dir, self.subject_id)
        self.pbr = pbr

    def get_probability_map_path(self, class_idx: int, atlas_name: str = 'AAL') -> str:
        """
        Returns the expected path for an existing 3D class probability map

        :param class_idx: class index
        :type class_idx: int
        :param atlas_name: name of the atlas used as template
        :type atlas_name: str
        :return: path to npy file
        :rtype: str
        """
        return os.path.join(self.results_dir, f'class_{class_idx}_{atlas_name}.npy')

    def get_probability_map(self, class_idx: int, atlas_name: str = 'AAL') -> np.ndarray:
        """
        Returns the 3D probability map for the chosen class over the chosen atlas as template

        :param class_idx: class index
        :type class_idx: int
        :param atlas_name: name of the atlas used as template
        :type atlas_name: str
        :return: 3D probability map for the chosen class
        :rtype: np.ndarray
        """
        path = self.get_probability_map_path(class_idx, atlas_name)
        if os.path.isfile(path):
            return np.load(path)
        else:
            print(f'Failed to load class {class_idx} probability map for {self.name}')

    def get_brain_matrix(self, class_idx: int, atlas_name: str = 'AAL') -> BrainMatrix:
        """
        Create a BrainMatrix instance with the chosen probability map

        :param class_idx: class index
        :type class_idx: int
        :param atlas_name: name of the atlas used as template
        :type atlas_name: str
        :return: probability map as BrainMatrix instance
        :rtype: BrainMatrix
        """
        probability_map = self.get_probability_map(class_idx, atlas_name)
        info_dict = {'subject': self, 'class': class_idx}
        return BrainMatrix(probability_map, info=info_dict)

    def get_all_probability_maps(self, atlas_name: str = 'AAL') -> list:
        """
        Returns a list of BrainMatrix instances for each class

        :param atlas_name: name of the atlas used as template
        :type atlas_name: str
        :return: all class probability maps
        :rtype: list of BrainMatrix instances
        """
        return [self.get_brain_matrix(class_idx, atlas_name) for class_idx in range(n_classes)]

    def __str__(self):
        return f'{self.name}/{self.scan_date}'

    def __eq__(self, other):
        return self.subject_id == other.subject_id

    @property
    def name(self):
        return self.subject_id[:4]

    @property
    def scan_date(self):
        return self.subject_id[4:]

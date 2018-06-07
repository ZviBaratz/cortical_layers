import os
import re

import numpy as np

from brain_matrix import BrainMatrix
from cfg import results_dir, n_classes


class Subject:
    _id = None
    name_id = None
    pbr = None

    def __init__(self, **kwargs):
        self.set_attributes(kwargs)
        if not self.id:
            raise ValueError('Subject instances must be instantiated with a valid ID!')
        self.results_dir = os.path.join(results_dir, self.id)

    def check_id(self, subject_id: str):
        return subject_id.isdigit() and len(subject_id) is 9

    def set_attributes(self, kwargs) -> None:
        for key, value in kwargs.items():
            key = key.replace(' ', '_').lower()
            setattr(self, key, value)

    def has_results_dir(self) -> bool:
        return os.path.isdir(self.results_dir)

    def has_probability_maps(self) -> bool:
        probability_map_paths = self.get_all_probability_map_paths()
        all_exist = all([os.path.isfile(path) for path in probability_map_paths])
        if all_exist:
            print(f'Found all probability maps for subject {self.id}!')
        else:
            print(f'Could not find subject {self.id} probability maps!')
        return all_exist

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

    def get_all_probability_map_paths(self, atlas_name: str = 'AAL') -> list:
        return [self.get_probability_map_path(class_idx, atlas_name) for class_idx in
                range(n_classes)]

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
        if path and os.path.isfile(path):
            return np.load(path)
        else:
            print(f'Failed to load class {class_idx} probability map for subject {self.id}')

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
        print(f'Retrieving class {class_idx} probability map...')
        probability_map = self.get_probability_map(class_idx, atlas_name)
        if isinstance(probability_map, np.ndarray):
            info_dict = {'subject': self, 'class': class_idx, 'atlas': atlas_name}
            print(f'Creating a BrainMatrix instance for class {class_idx}...')
            return BrainMatrix(probability_map, info=info_dict)

    def get_all_probability_maps(self, atlas_name: str = 'AAL') -> list:
        """
        Returns a list of BrainMatrix instances for each class

        :param atlas_name: name of the atlas used as template
        :type atlas_name: str
        :return: all class probability maps
        :rtype: list of BrainMatrix instances
        """
        if self.has_probability_maps():
            print('Generating brain matrix objects from serialized probability maps...')
            return [self.get_brain_matrix(class_idx, atlas_name) for class_idx in range(n_classes)]

    def __str__(self):
        return f'{self.name_id}/{self.id}'

    def __eq__(self, other) -> bool:
        return self.id == other.id

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        if self.check_id(value):
            self._id = value
        else:
            raise ValueError(f'Invalid ID: {value} - must be a 9 digit string!')

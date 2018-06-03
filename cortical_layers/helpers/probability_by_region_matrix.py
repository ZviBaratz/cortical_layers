import os

import numpy as np

from scipy.io import loadmat
from .brain_atlas import BrainAtlas

aal = BrainAtlas(name='AAL', path=os.path.abspath('./cortical_layers/templates/AAL1000.nii'))


class ProbabilityByRegionMatrix:
    _raw_data = None
    _data = None
    atlas_regions_axis = 0
    cortical_classes_axis = 1
    n_classes = 6
    data_key = 'results'

    def __init__(self, from_file: str = False, from_array: np.ndarray = False, atlas: BrainAtlas = aal):
        self.atlas = atlas
        if from_file:
            self.read_from_file(from_file)
        elif from_array:
            self.from_array(from_array)

    def read_from_file(self, path: str) -> None:
        self.data = loadmat(path)[self.data_key]

    def from_array(self, pbr_matrix: np.ndarray) -> None:
        self.data = pbr_matrix

    def save(self, path: str) -> None:
        np.save(path, self.data)

    def validate_data(self, data: np.ndarray):
        assert data.shape[self.cortical_classes_axis] == self.n_classes
        return True

    def get_data(self):
        return self.data

    def get_region_probability_dict(self, class_idx: int):
        return {region_id + 1: value for region_id, value in enumerate(self.data[:, class_idx])}

    def create_class_probability_map(self, class_idx: int):
        return self.atlas.convert_from_dict(self.get_region_probability_dict(class_idx))

    def create_all_class_probability_maps(self):
        return np.stack(self.create_class_probability_map(class_idx) for class_idx in
                        range(self.n_classes))

    def save_all_class_probability_maps(self, path: str):
        np.save(path, self.create_all_class_probability_maps())

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value: np.ndarray):
        if self.validate_data(value):
            self._data = value

    @property
    def n_regions(self):
        return self.atlas.n_regions


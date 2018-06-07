import os

import numpy as np

from scipy.io import loadmat
from .brain_atlas import BrainAtlas

aal = BrainAtlas(name='AAL', path=os.path.abspath('./cortical_layers/templates/AAL1000.nii'))


class ProbabilityByRegionMatrix:
    _raw_data = None
    _data = None
    path = ''
    atlas_regions_axis = 0
    class_idx_axis = 1
    n_classes = 6
    data_key = 'results'

    def __init__(self, from_file: str = False, from_array: np.ndarray = False,
                 atlas: BrainAtlas = aal):
        self.atlas = atlas

        if isinstance(from_file, str) and os.path.isfile(from_file):
            self.read_from_file(from_file)
        elif isinstance(from_array, np.ndarray):
            self.from_array(from_array)

    def read_from_file(self, path: str) -> None:
        if path.endswith('.mat'):
            self.data = loadmat(path)[self.data_key]
        elif path.endswith('.npy'):
            self.data = np.load(path)
        self.path = path

    def from_array(self, pbr_matrix: np.ndarray) -> None:
        self.data = pbr_matrix

    def save(self, path: str) -> None:
        np.save(path, self.data)
        self.path = path

    def validate_data(self, data: np.ndarray):
        assert data.shape[self.class_idx_axis] == self.n_classes
        return True

    def get_data(self) -> np.ndarray:
        return self.data

    def get_region_probability_dict(self, class_idx: int) -> dict:
        return {region_id + 1: value for region_id, value in enumerate(self.data[:, class_idx])}

    def create_class_probability_map(self, class_idx: int) -> np.ndarray:
        return self.atlas.convert_from_dict(self.get_region_probability_dict(class_idx))

    def save_class_probability_map(self, class_idx: int, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.isfile(path):
            np.save(path, self.create_class_probability_map(class_idx))
        else:
            print(f'{path} already exists! skipping...')

    def stack_all_class_probability_maps(self) -> np.ndarray:
        return np.stack(self.create_class_probability_map(class_idx) for class_idx in
                        range(self.n_classes))

    def save_all_class_probability_maps(self, path: str) -> None:
        for class_idx in range(self.n_classes):
            file_path = os.path.join(path, f'class_{class_idx}_{self.atlas.name}')
            self.save_class_probability_map(class_idx, file_path)

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

    @property
    def subject_id(self) -> str:
        if self.path:
            return str(os.path.basename(self.path).split('.')[0])
        else:
            return ''

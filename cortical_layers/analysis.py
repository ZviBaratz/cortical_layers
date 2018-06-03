import os

import numpy as np

from cortical_layers import cfg
from .helpers.data_loader import DataLoader
from .helpers.brain_atlas import BrainAtlas
from cortical_layers.helpers.probability_by_region_matrix import ProbabilityByRegionMatrix

data = DataLoader().read_data()


class CorticalLayersAnalysis:
    _mean_pbr = _stacked_data = None
    _mean_pbr_path = '/home/flavus/PycharmProjects/cortical_layers/cortical_layers/test/test_data/all_class_means_aal.npy'

    def __init__(self, probability_by_region_matrices: list = data):
        self.probability_by_region_matrices = probability_by_region_matrices

    def _get_stacked_data(self) -> np.ndarray:
        return np.stack(
            [pbr_matrix.read_data() for pbr_matrix in self.probability_by_region_matrices], axis=-1)

    def _get_mean_across_subjects(self) -> ProbabilityByRegionMatrix:
        return ProbabilityByRegionMatrix(from_array=self.stacked_data.mean(axis=2))

    def _load_mean_pbr(self) -> ProbabilityByRegionMatrix:
        if not isinstance(self._mean_pbr, ProbabilityByRegionMatrix):
            if os.path.isfile(self._mean_pbr_path):
                return ProbabilityByRegionMatrix(from_file=self._mean_pbr_path)
            else:
                mean_pbr = self._get_mean_across_subjects()
                mean_pbr.save(self._mean_pbr_path)
                return mean_pbr

    def get_class_over_atlas(self, pbr: ProbabilityByRegionMatrix, class_idx: int):
        return pbr.atlas.convert_from_dict(pbr.get_region_probability_dict(class_idx))

    def save_mean_pbr(self, file_name: str = None) -> None:
        if not file_name:
            file_name = self._mean_pbr_path
        print(f'Saving mean class probabilites over AAL to {file_name}...', end='\t')
        np.save(file_name, self.all_class_means_over_aal)
        print('done!')

    def get_all_class_means_over_aal_from_file(self, file_name: str = None):
        if not file_name:
            file_name = self._default_class_means_file_path
        print(f'Reading mean class probabilites over AAL template from {file_name}...', end='\t')
        pbr = ProbabilityByRegionMatrix(file_name)
        print('done!')
        return pbr

    @property
    def stacked_data(self) -> np.ndarray:
        if not isinstance(self._stacked_data, np.ndarray):
            self._stacked_data = self._get_stacked_data()
        return self._stacked_data

    @property
    def mean_pbr(self):
        if not self._mean_pbr:
            self._mean_pbr = self._load_mean_pbr()
        return self._mean_pbr

    @property
    def all_class_means_over_atlas(self):
        return

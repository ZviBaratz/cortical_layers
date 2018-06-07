import os

import numpy as np

from .helpers.data_loader import DataLoader
from cortical_layers.helpers.probability_by_region_matrix import ProbabilityByRegionMatrix

data = DataLoader().get_data()


class CorticalLayersAnalysis:
    _mean_pbr = _stacked_data = None
    results_dir = os.path.abspath('./cortical_layers/results')
    _mean_pbr_path = os.path.join(results_dir, 'summary', 'mean', 'mean_pbr_matrix.npy')

    def __init__(self, subjects: list = data):
        self.subjects = subjects
        self.serialize_results()

    def _get_stacked_pbrs(self) -> np.ndarray:
        return np.stack(
            [pbr_matrix.data for pbr_matrix in self.probability_by_region_matrices], axis=-1)

    def _get_mean_across_subjects(self) -> ProbabilityByRegionMatrix:
        return ProbabilityByRegionMatrix(from_array=self.stacked_pbrs.mean(axis=2))

    def _load_mean_pbr(self) -> ProbabilityByRegionMatrix:
        if not isinstance(self._mean_pbr, ProbabilityByRegionMatrix):
            if os.path.isfile(self._mean_pbr_path):
                return ProbabilityByRegionMatrix(from_file=self._mean_pbr_path)
            else:
                mean_pbr = self._get_mean_across_subjects()
                mean_pbr.save(self._mean_pbr_path)
                return mean_pbr

    def save_mean_probability_map(self, path: str) -> None:
        self.mean_pbr.save_all_class_probability_maps(path)

    def save_summary_probability_maps(self):
        path = os.path.join(self.results_dir, 'summary')
        self.save_mean_probability_map(os.path.join(path, 'mean'))

    def serialize_results(self):
        changes = False
        for subject in self.subjects:
            saved = subject.save_probability_maps()
            if saved and not changes:
                changes = True
        if changes:
            self.save_summary_probability_maps()


    @property
    def stacked_pbrs(self) -> np.ndarray:
        if not isinstance(self._stacked_data, np.ndarray):
            self._stacked_data = self._get_stacked_pbrs()
        return self._stacked_data

    @property
    def mean_pbr(self):
        if not isinstance(self._mean_pbr, ProbabilityByRegionMatrix):
            self._mean_pbr = self._load_mean_pbr()
        return self._mean_pbr

    @property
    def probability_by_region_matrices(self):
        return [subject.pbr for subject in self.subjects if subject.pbr is not None]

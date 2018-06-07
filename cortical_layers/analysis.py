import os

import numpy as np

from .cfg import results_dir
from .helpers.data_loader import DataLoader
from cortical_layers.helpers.probability_by_region_matrix import ProbabilityByRegionMatrix

data = DataLoader().get_data()


class CorticalLayersAnalysis:
    path_dict = {'pbr': {}}
    _mean_pbr = _stacked_data = None

    def __init__(self, subjects: list = data):
        self.subjects = subjects
        self.summary_dir = os.path.join(results_dir, 'summary')
        self.path_dict['pbr'] = {}
        self.path_dict['pbr']['mean'] = os.path.join(self.summary_dir, 'mean', 'mean_pbr_matrix.npy')
        self.path_dict['atlas_projection'] = {}
        self.path_dict['atlas_projection']['AAL'] = {}
        self.path_dict['atlas_projection']['AAL']['mean'] = os.path.join(self.summary_dir, 'AAL', 'mean')
        self.serialize_results()

    def get_stacked_pbrs(self) -> np.ndarray:
        """
        Returns all probability by region matrices stacked in one array

        :return: stacked probability by region matrix (region x class x subject)
        :rtype: np.ndarray
        """
        return np.stack([pbr.data for pbr in self.probability_by_region_matrices], axis=-1)

    def create_mean_pbr(self) -> ProbabilityByRegionMatrix:
        """
        Saves and returns a ProbabilityByRegionMatrix instance representing the subject's mean

        :return: mean probability by region across subjects
        :rtype: ProbabilityByRegionMatrix
        """
        mean_pbr = ProbabilityByRegionMatrix(from_array=self.stacked_pbrs.mean(axis=2))
        mean_pbr.save(self.path_dict['pbr']['mean'])
        return mean_pbr

    def load_mean_pbr(self, autocreate=True) -> ProbabilityByRegionMatrix:
        """
        Returns an existing mean ProbabilityByRegionMatrix instance or creates it

        :return: mean probability by region across subjects
        :rtype: ProbabilityByRegionMatrix
        """
        if os.path.isfile(self.path_dict['pbr']['mean']):
            return ProbabilityByRegionMatrix(from_file=self.path_dict['pbr']['mean'])
        if autocreate:
            return self.create_mean_pbr()

    def save_summary_probability_maps(self) -> None:
        """
        Saves summary probability maps projected onto the associated brain atlas
        """
        atlas_name = self.mean_pbr.atlas.name
        self.mean_pbr.save_all_class_probability_maps(self.path_dict['atlas_projection'][atlas_name]['mean'])

    def serialize_results(self):
        for subject in self.subjects:
            subject.save_probability_maps()
        self.save_summary_probability_maps()

    @property
    def stacked_pbrs(self) -> np.ndarray:
        if not isinstance(self._stacked_data, np.ndarray):
            self._stacked_data = self.get_stacked_pbrs()
        return self._stacked_data

    @property
    def mean_pbr(self):
        if not isinstance(self._mean_pbr, ProbabilityByRegionMatrix):
            self._mean_pbr = self.load_mean_pbr()
        return self._mean_pbr

    @property
    def probability_by_region_matrices(self):
        return [subject.pbr for subject in self.subjects if subject.pbr is not None]

import os

import numpy as np

from .cfg import cortical_layers_data
from .helpers.dao import DataAccessObject
from .helpers.cortical_layers.probability_by_region_matrix import ProbabilityByRegionMatrix

dao = DataAccessObject()


class CorticalLayersAnalysis:
    _mean_pbr = None
    _std_pbr = None
    _stacked_data = None
    subjects_axis = 2

    def __init__(self, dao: DataAccessObject = dao):
        self.dao = dao
        self.summary_dir = os.path.join(cortical_layers_data, 'summary')

    def get_stacked_pbrs(self) -> np.ndarray:
        """
        Returns all probability by region matrices stacked in one array

        :return: stacked probability by region matrix (region x class x subject)
        :rtype: np.ndarray
        """
        return np.stack(
            [subject.pbr.data for subject in self.dao.subjects if hasattr(subject, 'pbr')], axis=-1)

    def create_mean_pbr(self) -> ProbabilityByRegionMatrix:
        """
        Returns a ProbabilityByRegionMatrix instance representing the mean across subjects

        :return: mean probability by region across subjects
        :rtype: ProbabilityByRegionMatrix
        """
        return ProbabilityByRegionMatrix(from_array=self.stacked_pbrs.mean(axis=self.subjects_axis))

    def create_std_pbr(self) -> ProbabilityByRegionMatrix:
        """
        Returns a ProbabilityByRegionMatrix instance representing the STD across subjects

        :return: STD of class probability by region across subjects
        :rtype: ProbabilityByRegionMatrix
        """
        return ProbabilityByRegionMatrix(from_array=self.stacked_pbrs.std(axis=self.subjects_axis))

    @property
    def stacked_pbrs(self) -> np.ndarray:
        if not isinstance(self._stacked_data, np.ndarray):
            self._stacked_data = self.get_stacked_pbrs()
        return self._stacked_data

    @property
    def mean_pbr(self):
        if not isinstance(self._mean_pbr, ProbabilityByRegionMatrix):
            self._mean_pbr = self.create_mean_pbr()
        return self._mean_pbr

    @property
    def std_pbr(self):
        if not isinstance(self._std_pbr, ProbabilityByRegionMatrix):
            self._std_pbr = self.create_std_pbr()
        return self._std_pbr

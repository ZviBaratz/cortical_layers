import glob
import os

import numpy as np
import pandas as pd
import statsmodels.api as sm

from .cfg import n_classes, results_dir
from .probability_by_region_matrix import ProbabilityByRegionMatrix
from .probability_map import ProbabilityMap


class CorticalLayersAnalysis:
    _mean_pbr = None
    _mean_probability_maps = None
    _std_pbr = None
    _stacked_data = None
    subjects_axis = 2

    def __init__(self, pbr_matrices: list):
        self.pbrs = pbr_matrices

    def get_pbr_by_subject_id(self, subject_id: str):
        result = [pbr for pbr in self.pbrs if pbr.subject_id == subject_id]
        if result:
            return result[0]

    def get_stacked_pbrs(self) -> np.ndarray:
        """
        Returns all probability by region matrices stacked in one array

        :return: stacked probability by region matrix (region x class x subject)
        :rtype: np.ndarray
        """
        return np.stack([pbr.data for pbr in self.pbrs], axis=-1)

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

    def create_mean_probability_map(self, class_idx: int) -> ProbabilityMap:
        return self.mean_pbr.create_class_probability_map(class_idx)

    def create_mean_probability_maps(self) -> list:
        return [self.create_mean_probability_map(class_idx) for class_idx in range(n_classes)]

    def save_probability_maps(self, probability_maps: list, path: str) -> None:
        for probability_map in probability_maps:
            class_idx = probability_map.class_idx
            atlas_name = probability_map.atlas.name
            file_path = os.path.join(path, f'class_{class_idx}_{atlas_name}')
            probability_map.save(file_path)

    def load_probability_maps(self, paths: list):
        result = []
        for path in sorted(paths):
            if os.path.isfile(path):
                name = os.path.basename(path)
                _, class_idx, _ = name.split('_')
                data = np.load(path)
                result.append(ProbabilityMap(data, class_idx))
        return result

    def load_mean_probability_maps(self):
        dir_path = os.path.join(results_dir, 'mean')
        files = glob.glob(os.path.join(dir_path, '*.npy'))
        if os.path.isdir(dir_path) and files:
            return self.load_probability_maps(files)

    def calculate_region_mlr_model(self, region_idx: int, scores: pd.DataFrame):
        columns = [f'class_{class_idx}' for class_idx in range(1, n_classes + 1)]
        index = [pbr.subject_id for pbr in self.pbrs]
        X = pd.DataFrame(columns=columns, index=index)
        scores = scores[scores.index.isin(X.index)]
        for subject_id, score in scores.iterrows():
            pbr = self.get_pbr_by_subject_id(subject_id)
            if isinstance(pbr, ProbabilityByRegionMatrix):
                X.loc[subject_id] = pbr.data[region_idx, :]
        X = X.dropna()
        model = sm.OLS(scores, X.astype(float)).fit()
        # predictions = model.predict(X)
        return model #, predictions

    def calculate_linear_model_dict(self, scores: pd.DataFrame):
        results_dict = {'region': [], 'rsquared': [], 'rsquared_adj': [], 'pvalues': []}
        for region_idx in range(1000):
            model = self.calculate_region_mlr_model(region_idx, scores)
            results_dict['region'].append(region_idx)
            results_dict['rsquared'].append(model.rsquared)
            results_dict['rsquared_adj'].append(model.rsquared_adj)
            results_dict['pvalues'].append(model.pvalues)
        return results_dict

    def calculate_linear_model(self, scores: pd.DataFrame):
        results_dict = self.calculate_linear_model_dict(scores)
        df = pd.DataFrame.from_dict(results_dict)
        df = df.set_index('region')
        return df

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

    @property
    def mean_probability_maps(self):
        if not isinstance(self._mean_probability_maps, list):
            serialized = self.load_mean_probability_maps()
            if serialized:
                self._mean_probability_maps = serialized
            else:
                self._mean_probability_maps = self.create_mean_probability_maps()
                path = os.path.join(results_dir, 'mean')
                if not os.path.isdir(path):
                    os.makedirs(path)
                self.save_probability_maps(self._mean_probability_maps, path)
        return self._mean_probability_maps

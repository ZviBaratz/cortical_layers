import numpy as np
import pandas as pd

from .data_classes.data_loader import DataLoader
from .data_classes.cortical_layers.analysis import CorticalLayersAnalysis
from .data_classes.cortical_layers.probability_map import ProbabilityMap
from .data_classes.cortical_layers.cfg import n_classes
from .data_classes.subject import Subject

data_loader = DataLoader()


class DataAccessObject:
    _chosen_subject = None
    _results_set = None
    _pbrs = None

    def __init__(self, subjects: list = data_loader.subjects):
        """
        This class handles data access

        :param subjects: subjects data
        :type subjects: list of subject instances
        """
        self.subjects = subjects
        self.cla = CorticalLayersAnalysis(self.pbrs)

    def get_subject_by_id(self, subject_id: str) -> Subject:
        return data_loader.get_subject_by_id(subject_id)

    def get_scores(self, measurement_name: str):
        scores_dict = {
        subject.id: subject.measurements.get_measurement_data(measurement_name)['value'].values[0]
        for subject in self.subjects}
        return pd.DataFrame(data=list(scores_dict.values()), index=list(scores_dict.keys()))

    def get_neo_scores(self, trait: str):
        scores_dict = {subject.id: getattr(subject.neo_ffi, trait) for subject in self.subjects if hasattr(subject, 'neo_ffi')}
        return pd.DataFrame(data=list(scores_dict.values()), index=list(scores_dict.keys()))

    def get_probability_by_region_matrices(self):
        return [subject.pbr for subject in self.subjects if hasattr(subject, 'pbr')]

    def get_results_set(self, identifier: str) -> list:
        """
        Get a results set (list of ordered class probability brain matrices) by identifier

        :param identifier: results set identifier
        :type identifier: str
        :return: desired results set
        :rtype: list  of BrainMatrix instances
        """
        # Get summary results
        probability_maps = None
        if identifier == 'mean':
            print('Retrieving class mean probabilites result set...', end='\t')
            probability_maps = self.cla.mean_probability_maps
            print('done!')
            return probability_maps

        # Get single subject results
        subject = self.get_subject_by_id(identifier)
        if isinstance(subject, Subject):
            print(f'Retrieving result set for subject {subject.id}...', end='\t')
            if hasattr(subject, 'pbr'):
                probability_maps = subject.pbr.create_all_class_probability_maps()
            print('done!')
            return probability_maps

        # Handle non found
        print(f'Invalid results set: {identifier}!')

    def validate_results_set(self, value) -> bool:
        """
        Validates a results set before it is set

        :param value: potential results set
        :return:
        """
        print('Validating assigned results set...', end='\t')
        if value is None or len(value) is 0:
            print('done!')
            return True
        is_list = isinstance(value, list)
        of_pmaps = all([isinstance(obj, ProbabilityMap) for obj in value])
        assert is_list and of_pmaps, 'Results set must be a list of BrainMatrix instances'
        assert len(value) is n_classes, f'Results set must be of length {n_classes}'
        print('done!')
        return True

    def get_slice(self, plane: str, class_idx: int, i_slice: int) -> np.ndarray:
        """
        Returns a slice image from the current results set according to the parameters

        :param plane: 'sagittal', 'coronal' or 'horizontal'
        :type plane: str
        :param class_idx: index of the cortical class
        :type class_idx: int
        :param i_slice: index of the desired slice
        :type i_slice: int
        :return: slice image
        :rtype: np.ndarray
        """
        return self.results_set[class_idx].create_slice(plane, i_slice)

    def get_subject_attributes_df(self):
        dicts = [subject.to_dict() for subject in self.subjects]
        df = pd.DataFrame(dicts)
        df = df.set_index('id')
        return df

    @property
    def chosen_subject(self) -> Subject:
        return self._chosen_subject

    @chosen_subject.setter
    def chosen_subject(self, value) -> None:
        if isinstance(value, Subject):
            self._chosen_subject = value

    @property
    def results_set(self) -> list:
        return self._results_set

    @results_set.setter
    def results_set(self, value) -> None:
        if self.validate_results_set(value):
            self._results_set = value

    @property
    def pbrs(self):
        if not isinstance(self._pbrs, list):
            self._pbrs = self.get_probability_by_region_matrices()
        return self._pbrs

import glob
import os

import numpy as np
import pandas as pd

from brain_matrix import BrainMatrix
from cfg import raw_data_dir, results_dir, n_classes, subjects_data_path
from scipy.io import loadmat
from subject import Subject
from summary_results import SummaryResults

subjects_df = pd.read_excel(subjects_data_path, sheet_name='Subjects', index_col=0)



class DataAccessObject:
    _results_set = None
    _subjects = None
    _selected_subject = None
    raw_data_format = 'mat'
    raw_data_key = 'results'
    summary = SummaryResults()

    def __init__(self, subjects_df: pd.DataFrame = subjects_df):
        self.subjects_df = subjects_df

    def create_subject_instance(self, subject_row: tuple) -> Subject:
        subject_id = str(subject_row[0]).zfill(9)
        attributes = subject_row[1]
        return Subject(id=subject_id, **attributes.to_dict())

    def load_subjects(self, df: pd.DataFrame) -> list:
        return [self.create_subject_instance(subject_row) for subject_row in df.iterrows()]

    def get_raw_data_paths(self) -> list:
        """
        Returns a sorted list of raw data files (class probability by region matrices as mat files)

        :return: class probability by region file paths list
        :rtype: list of paths
        """
        return sorted(glob.glob(os.path.join(raw_data_dir, f'*.{self.raw_data_format}')))

    def load_pbr_from_mat(self, path: str) -> np.ndarray:
        """
        Loads class probability by region matrix from mat file

        :param path: mat file path
        :type path: str
        :return: class probability by region matrix
        :rtype: np.ndarray
        """
        return loadmat(path)[self.raw_data_key]

    def get_subject_by_id(self, subject_id: str) -> Subject:
        """
        Get subject instances by subject ID (name + scan_date)

        :param subject_id: subject unique identifier
        :type subject_id: str
        :return: subject instance
        :rtype: Subject
        """
        result = [subject for subject in self.subjects if subject.id == subject_id]
        if len(result) is not 0:
            return result[0]

    def get_results_set(self, identifier: str) -> list:
        """
        Get a results set (list of ordered class probability brain matrices) by identifier

        :param identifier: results set identifier
        :type identifier: str
        :return: desired results set
        :rtype: list  of BrainMatrix instances
        """
        # Get summary results
        if identifier == 'mean':
            print('Retrieving class mean probabilites result set...', end='\t')
            all_class_means = self.summary.get_all_class_means()
            print('done!')
            return all_class_means

        # Get single subject results
        subject = self.get_subject_by_id(identifier)
        if isinstance(subject, Subject):
            print(f'Retrieving result set for subject {subject.id}...')
            probability_maps = subject.get_all_probability_maps()
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
        of_brain_matrices = all([isinstance(obj, BrainMatrix) for obj in value])
        assert is_list and of_brain_matrices, 'Results set must be a list of BrainMatrix instances'
        assert len(value) is n_classes, f'Results set must be of length {n_classes}'
        print('done!')
        return True

    def get_class_brain_martix(self, class_idx: int) -> BrainMatrix:
        """
        Returns the BrainMatrix instance of the desired class

        :param class_idx: class index
        :type class_idx: str
        :return: class probability brain matrix
        :rtype: BrainMatrix
        """
        return self.results_set[class_idx]

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
        return self.get_class_brain_martix(class_idx).create_slice(plane, i_slice)

    @property
    def subjects(self) -> list:
        if not isinstance(self._subjects, list):
            self._subjects = self.load_subjects(self.subjects_df)
        return self._subjects

    @subjects.setter
    def subjects(self, value: pd.DataFrame) -> None:
        try:
            self._subjects = self.load_subjects(value)
        except Exception as e:
            print(e.args)
            print('Failed to initialize subject instances from DataFrame!')

    @property
    def raw_data_paths(self) -> list:
        """
        Returns all probability by region matrices

        :return: list of probability by region matrix files
        :rtype: list
        """
        return self.get_raw_data_paths()

    @property
    def selected_subject(self):
        return self._selected_subject

    @selected_subject.setter
    def selected_subject(self, value):
        if isinstance(value, Subject):
            self._selected_subject = value

    @property
    def results_set(self) -> list:
        """
        Current results set to be accessed

        :return: all class probability brain matrices
        :rtype: list of BrainMatrix instances
        """
        if not isinstance(self._results_set, list):
            # Defaults to mean
            self._results_set = None
        return self._results_set

    @results_set.setter
    def results_set(self, value: list) -> None:
        """
        Results set setter - validates a list of BrainMatrix instances to be set as results set

        :param value: new results set
        :type value: list of BrainMatrix instances
        """
        if self.validate_results_set(value):
            self._results_set = value
            print('Successfully changed results set')

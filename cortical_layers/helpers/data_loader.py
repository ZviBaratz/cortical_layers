import glob
import os

import pandas as pd

from .probability_by_region_matrix import ProbabilityByRegionMatrix
from .subject import Subject


subjects_data_path = '/home/flavus/PycharmProjects/cortical_layers/cortical_layers/Subjects.xlsx'
subjects = pd.read_excel(subjects_data_path, sheet_name='Subjects', index_col=0)
measurements = pd.read_excel(subjects_data_path, sheet_name='Measurements', index_col=0)

# pbr_data_path = '/media/flavus/data/results/cortical_layers'
pbr_data_path = '/home/flavus/PycharmProjects/cortical_layers/cortical_layers/test/test_data'

class DataLoader:
    _subjects = []
    _probability_by_region_matrix_instances = []
    data_files_format = 'mat'
    subjects_axis = 2

    def __init__(self, subjects_df: pd.DataFrame = subjects, pbr_path: str = pbr_data_path):
        self.df = subjects_df
        self.pbr_path = pbr_path
        self.add_pbrs_to_subjects()

    def create_subject_instances(self, subject_row: tuple) -> Subject:
        subject_id = str(subject_row[0]).zfill(9)
        attributes = subject_row[1]
        return Subject(id=subject_id, **attributes.to_dict())

    def load_subjects(self, df: pd.DataFrame) -> list:
        return [self.create_subject_instances(subject_row) for subject_row in df.iterrows()]

    def get_pbr_file_paths(self) -> list:
        return sorted(glob.glob(os.path.join(self.pbr_path, f'*.{self.data_files_format}')))

    def get_probability_by_region_matrices(self) -> list:
        return [ProbabilityByRegionMatrix(from_file=file) for file in self.get_pbr_file_paths()]

    def get_subject_by_id(self, subject_id: str) -> Subject:
        result = [subject for subject in self.subjects if subject.id == subject_id]
        if result:
            return result[0]

    def add_pbrs_to_subjects(self) -> None:
        for pbr in self.probability_by_region_matrix_instances:
            subject = self.get_subject_by_id(pbr.subject_id)
            if subject:
                subject.add_class_probability_by_region_matrix(pbr)
            else:
                print(f'Failed to locate subject {pbr.subject_id}, skipping...')

    def get_data(self) -> list:
        try:
            data = self.subjects
            print(f'Successfully loaded data for {len(data)} subjects!')
            return data
        except Exception as e:
            print('Failed to read subjects data!')
            print(e)

    @property
    def probability_by_region_matrix_instances(self) -> list:
        if not self._probability_by_region_matrix_instances:
            self._probability_by_region_matrix_instances = self.get_probability_by_region_matrices()
        return self._probability_by_region_matrix_instances

    @property
    def subjects(self) -> list:
        if not self._subjects:
            self._subjects = self.load_subjects(self.df)
        return self._subjects

    @subjects.setter
    def subjects(self, value: pd.DataFrame) -> None:
        try:
            self._subjects = self.load_subjects(value)
        except Exception as e:
            print(e)
            print('Failed to initialize subject instances from DataFrame!')


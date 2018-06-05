import glob
import os

from .probability_by_region_matrix import ProbabilityByRegionMatrix
from .subject import Subject

# data_path = '/media/flavus/data/results/cortical_layers'
data_path = '/home/flavus/PycharmProjects/cortical_layers/cortical_layers/test/test_data'


class DataLoader:
    data_files_format = 'mat'
    subjects_axis = 2

    def __init__(self, path: str = data_path):
        self.path = path

    def get_data_file_paths(self) -> list:
        return sorted(glob.glob(os.path.join(self.path, f'*.{self.data_files_format}')))

    def get_probability_by_region_matrices(self) -> list:
        return [ProbabilityByRegionMatrix(from_file=file) for file in self.get_data_file_paths()]

    def get_subjects(self) -> list:
        return [Subject(**pbr.get_subject_attributes_from_file_name(), pbr=pbr) for pbr in
                self.get_probability_by_region_matrices()]

    def get_data(self):
        try:
            data = self.get_subjects()
            print(f'Successfully loaded data for {len(data)} subjects!')
            return data
        except Exception as e:
            print(f'Failed to read data from {self.path}!')
            print(e)

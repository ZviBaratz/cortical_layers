import glob
import os

import numpy as np
from .subject_layers_matrix import SubjectLayersMatrix

# data_path = '/media/flavus/data/results/cortical_layers'
data_path = '/home/flavus/PycharmProjects/cortical_layers/cortical_layers/test/test_data'


class DataLoader:
    data_files_format = 'mat'
    subjects_axis = 2

    def __init__(self, path: str = data_path):
        self.path = path

    def get_data_file_paths(self) -> list:
        return glob.glob(os.path.join(self.path, f'*.{self.data_files_format}'))

    def get_data_matrices(self) -> list:
        return [SubjectLayersMatrix(file).get_data() for file in self.get_data_file_paths()]

    def read_data(self) -> np.ndarray:
        try:
            data = np.dstack(self.get_data_matrices())
            print(f'Successfully loaded data for {data.shape[2]} subjects!')
            return data
        except Exception as e:
            print(f'Failed to read data from {self.path}!')
            print(e)

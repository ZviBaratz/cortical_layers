import glob
import os

from cortical_layers.helpers.cortical_layers.probability_by_region_matrix import ProbabilityByRegionMatrix
from cortical_layers.cfg import cortical_layers_data

FILE_FORMAT = 'mat'


class CorticalLayersResults:
    def __init__(self, path: str = cortical_layers_data):
        self.path = path

    def get_files(self) -> list:
        return sorted(glob.glob(os.path.join(self.path, f'*.{FILE_FORMAT}')))

    def get_probability_by_region_matrix_instances(self) -> list:
        return [ProbabilityByRegionMatrix(from_file=file) for file in self.get_files()]
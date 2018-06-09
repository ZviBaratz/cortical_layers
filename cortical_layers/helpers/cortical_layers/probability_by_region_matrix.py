import os

import numpy as np

from scipy.io import loadmat
from cortical_layers.helpers.cortical_layers.brain_atlas import BrainAtlas
from cortical_layers.cfg import results_dir, n_classes, atlas

MAT_DATA_KEY = 'results'


class ProbabilityByRegionMatrix:
    _data = None
    _path = ''
    atlas_regions_axis = 0
    class_idx_axis = 1

    def __init__(self, from_file: str = False, from_array: np.ndarray = False,
                 atlas: BrainAtlas = atlas):
        """
        Cortical class probability by region utility class

        :param from_file: load class PBR data from path
        :type from_file: str
        :param from_array: set class PBR data as array
        :type from_array: np.ndarray
        :param atlas: associated brain atlas
        :type atlas: BrainAtlas
        """
        self.atlas = atlas
        self.load_data(from_file, from_array)

    def load_data(self, from_file, from_array):
        if isinstance(from_file, str) and os.path.isfile(from_file):
            self.read_from_file(from_file)
        elif isinstance(from_array, np.ndarray):
            self.from_array(from_array)
        else:
            raise ValueError('Invalid input!')

    def read_from_file(self, path: str) -> None:
        """
        Loads data from file and updates path

        :param path: probability by region data
        :type path: str
        :return:
        """
        # Read .mat files
        if path.endswith('.mat'):
            self.data = loadmat(path)[MAT_DATA_KEY]
        # Read .npy files
        elif path.endswith('.npy'):
            self.data = np.load(path)
        # Update path
        self.path = path

    def from_array(self, pbr_matrix: np.ndarray) -> None:
        """
        Set probability be region data from numpy array

        :param pbr_matrix: class probability by region
        :type pbr_matrix: np.ndarray
        :return:
        """
        self.data = pbr_matrix

    def save(self, path: str = None) -> None:
        """
        Save probability by region data to file and update path

        :param path: destination path
        :type path: str
        :return:
        """
        if not path:
            path = self.default_path
        os.makedirs(path, exist_ok=True)
        np.save(path, self.data)
        self.path = path

    def check_n_classes(self, data: np.ndarray) -> bool:
        """
        Validate the number of classes in the appropriate axis of an array

        :param data: class probability by region matrix
        :type data: np.ndarray
        :return: validation result
        :rtype: bool
        """
        return data.shape[self.class_idx_axis] == n_classes

    def check_n_regions(self, data: np.ndarray):
        n_data_regions = data.shape[self.atlas_regions_axis]
        if n_data_regions is not self.atlas.n_regions:
            print(f'WARNING: ProbabilityByRegionMatrix data contains {n_data_regions} regions but '
                  f'atlas has {self.atlas.n_regions}!')
            return False
        return True

    def validate_data(self, data: np.ndarray) -> bool:
        """
        Run all necessary validations for probability by region data

        :param data: class probability by region matrix
        :type data: np.ndarray
        :return: validation result
        :rtype: bool
        """
        assert self.check_n_classes(
            data), f'Data must have {n_classes} in the {self.class_idx_axis} axis!'
        self.check_n_regions(data)
        return True

    def get_region_probability_dict(self, class_idx: int) -> dict:
        """
        Create a dictionary of values by region that may be passed to a BrainAtlas instance
        for conversion

        :param class_idx: class index
        :type class_idx: int
        :return: class probability by region
        :rtype: dict
        """
        return {region_id + 1: value for region_id, value in enumerate(self.data[:, class_idx])}

    def create_class_probability_map(self, class_idx: int) -> np.ndarray:
        """
        Creates a projection of the class probabilities onto the appropriate atlas template

        :param class_idx: class index
        :type class_idx: int
        :return: probability map
        :rtype: np.ndarray
        """
        return self.atlas.convert_from_dict(self.get_region_probability_dict(class_idx))

    def save_class_probability_map(self, class_idx: int, path: str) -> None:
        """
        Creates and saves the class probability map projected onto the appropriate atlas template
        to the desired destination

        :param class_idx: class index
        :type class_idx: int
        :param path: destination path
        :type path: str
        :return:
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        np.save(path, self.create_class_probability_map(class_idx))

    def save_all_class_probability_maps(self, path: str) -> None:
        """
        Creates and saves all class probability maps to the desired destination

        :param path: destination path
        :type path: str
        :return:
        """
        if os.path.isdir(path):
            for class_idx in range(n_classes):
                file_path = os.path.join(path, f'class_{class_idx}_{self.atlas.name}')
                self.save_class_probability_map(class_idx, file_path)
        else:
            raise NotADirectoryError(f'{path} is not a valid directory!')

    @property
    def default_path(self) -> str:
        """
        Default path for subject results

        :return: default destination path
        :rtype: str
        """
        return os.path.join(results_dir, self.subject_id)

    @property
    def path(self) -> str:
        """
        Returns the data path

        :return: class probability by region matrix data
        :rtype: str
        """
        return self._path

    @path.setter
    def path(self, value):
        """
        Validates a path exists before setting is as the data path

        :param value: data path
        :type value: str
        :return:
        """
        if os.path.isfile(value):
            self._path = value
        else:
            raise FileNotFoundError('Path must be set to an existing file!')

    @property
    def saved(self) -> bool:
        """
        Checks whether the data is serialized

        :return: boolean result
        :rtype: bool
        """
        if self.path and os.path.isfile(self.path):
            return True
        return False

    @property
    def data(self):
        """
        Returns class probability by region matrix data

        :return:
        """
        return self._data

    @data.setter
    def data(self, value: np.ndarray):
        """
        Validates matrix data to be set as class probability by region data

        :param value: class probability by region matrix
        :type value: np.ndarray
        :return:
        """
        if self.validate_data(value):
            self._data = value

    @property
    def n_regions(self) -> int:
        """
        Returns the number of regions in the associated brain atlas

        :return: number of brain atlas regions
        :rtype: int
        """
        return self.data.shape[self.atlas_regions_axis]

    @property
    def subject_id(self) -> str:
        """
        Infer subject ID from file name

        :return: subject ID
        :rtype: str
        """
        if self.path:
            return str(os.path.basename(self.path).split('.')[0])
        else:
            return ''

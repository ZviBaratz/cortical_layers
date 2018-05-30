import os

import nibabel as nib
import numpy as np

from cortical_layers import cfg
from .data_loader import DataLoader
from .subject_layers_matrix import SubjectLayersMatrix

data = DataLoader().read_data()


class CorticalLayersAnalysis:
    _subjects_mean = _aal_1000 = _all_class_means_over_aal = _surface = None
    _default_class_means_file_path = '/home/flavus/PycharmProjects/cortical_layers/cortical_layers/test/test_data/all_class_means_aal.npy'

    def __init__(self, data: np.ndarray = data):
        self.data = data

    def get_mean_across_subjects(self):
        return self.data.mean(axis=2)

    def get_class_mean_over_aal(self, cortical_class: int):
        if self._all_class_means_over_aal:
            return self.all_class_means_over_aal[:, :, :, cortical_class]
        else:
            result = np.zeros(self.aal_1000.shape).ravel()
            aal = self.aal_1000.ravel()
            for i_aal in range(self.n_regions):
                result[aal == i_aal + 1] = self.subjects_mean[i_aal, cortical_class]
            return result.reshape(self.aal_1000.shape)

    def get_all_class_means_over_aal(self):
        print('Generating mean class probabilities over an AAL template...', end='\t')
        result = np.stack(
            [self.get_class_mean_over_aal(i_class) for i_class in range(self.n_classes)], axis=-1)
        print('done!')
        return result

    def save_all_class_means_over_aal(self, file_name: str = None) -> None:
        if not file_name:
            file_name = self._default_class_means_file_path
        print(f'Saving mean class probabilites over AAL to {file_name}...', end='\t')
        np.save(file_name, self.all_class_means_over_aal)
        print('done!')

    def get_all_class_means_over_aal_from_file(self, file_name: str = None):
        if not file_name:
            file_name = self._default_class_means_file_path
        print(f'Reading mean class probabilites over AAL template from {file_name}...', end='\t')
        data = np.load(file_name)
        print('done!')
        return data

    @property
    def n_classes(self):
        return self.data.shape[SubjectLayersMatrix.cortical_classes_axis]

    @property
    def n_regions(self):
        return self.data.shape[SubjectLayersMatrix.atlas_regions_axis]

    @property
    def aal_1000(self):
        if not isinstance(self._aal_1000, np.ndarray):
            self._aal_1000 = nib.load(cfg.aal_1000_path).get_data()
        return self._aal_1000

    @property
    def surface(self):
        if not isinstance(self._surface, np.ndarray):
            self._surface = nib.load(cfg.surface_template_path).get_data()
        return self._surface

    @property
    def subjects_mean(self):
        if not isinstance(self._subjects_mean, np.ndarray):
            self._subjects_mean = self.get_mean_across_subjects()
        return self._subjects_mean

    @property
    def all_class_means_over_aal(self):
        if not isinstance(self._all_class_means_over_aal, np.ndarray):
            if os.path.isfile(self._default_class_means_file_path):
                self._all_class_means_over_aal = self.get_all_class_means_over_aal_from_file()
            else:
                self._all_class_means_over_aal = self.get_all_class_means_over_aal()
                self.save_all_class_means_over_aal()
        return self._all_class_means_over_aal

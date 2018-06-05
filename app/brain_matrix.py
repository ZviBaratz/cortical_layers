import numpy as np


class BrainMatrix:
    slice_planes = ['sagittal', 'coronal', 'horizontal']

    def __init__(self, data: np.ndarray, info: dict = None):
        self.data = data
        self.info = info

    def get_sagittal_slice(self, i_slice: int):
        return np.fliplr(np.rot90(self.data[i_slice, :, :], 3))

    def get_coronal_slice(self, i_slice: int):
        return np.rot90(self.data[:, i_slice, :], 3)

    def get_horizontal_slice(self, i_slice: int):
        return np.rot90(self.data[:, :, i_slice], 3)

    def create_slice(self, plane: str, i_slice: int):
        return self.get_slicer_function(plane)(i_slice)

    def get_slicer_function(self, plane: str):
        return getattr(self, f'get_{plane}_slice')

    def get_multi_planar(self, i_sagittal: int, i_coronal: int, i_horizontal: int):
        return [self.get_sagittal_slice(i_sagittal),
                self.get_coronal_slice(i_coronal),
                self.get_horizontal_slice(i_horizontal)]

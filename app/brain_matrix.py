import numpy as np

from bokeh.models import ColumnDataSource


class BrainMatrix:
    slice_planes = ['sagittal', 'coronal', 'horizontal']

    def __init__(self, data: np.ndarray, info: dict):
        self.data = data
        self.info = info

    def get_sagittal_slice(self, i_slice: int):
        return np.fliplr(np.rot90(self.data[i_slice, :, :], 3))

    def get_coronal_slice(self, i_slice: int):
        return np.rot90(self.data[:, i_slice, :], 3)

    def get_horizontal_slice(self, i_slice: int):
        return np.rot90(self.data[:, :, i_slice], 3)

    def get_slice(self, plane: str, i_slice: int):
        return self.get_slicer_function(plane)(i_slice)

    def get_slicer_function(self, plane: str):
        return getattr(self, f'get_{plane}_slice')

    def create_slice_cds(self, slice: np.ndarray):
        return ColumnDataSource(dict(image=[slice]))

    def get_multi_planar(self, i_sagittal: int, i_coronal: int, i_horizontal: int):
        return [self.get_sagittal_slice(i_sagittal),
                self.get_coronal_slice(i_coronal),
                self.get_horizontal_slice(i_horizontal)]

    def create_multi_planar_cds(self, i_sagittal: int, i_coronal: int, i_horizontal: int):
        slices = self.get_multi_planar(i_sagittal, i_coronal, i_horizontal)
        slices = [self.create_slice_cds(slice) for slice in slices]
        return dict(zip(self.slice_planes, slices))


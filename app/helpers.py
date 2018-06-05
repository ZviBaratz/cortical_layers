import numpy as np

from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Div
from typing import Iterable


class AllClassAALHandler:
    info_template = '''
    Min: {}<br />
    Max: {}<br />
    Mean: {}<br />
    STD: {}<br />
    '''
    info_functions = ['min', 'max', 'mean', 'std']
    slice_planes = ['sagittal', 'coronal', 'horizontal']

    def __init__(self, image: np.ndarray):
        self.image = image

    def get_sagittal_slice(self, slice: int, class_idx: int):
        return np.fliplr(np.rot90(self.image[slice, :, :, class_idx], 3))

    def get_coronal_slice(self, slice: int, class_idx: int):
        return np.rot90(self.image[:, slice, :, class_idx], 3)

    def get_horizontal_slice(self, slice: int, class_idx: int):
        return np.rot90(self.image[:, :, slice, class_idx], 3)

    def get_slice(self, plane: str, slice: int, class_idx: int):
        return self.get_slicer_function(plane)(slice, class_idx)

    def get_slicer_function(self, plane: str):
        return getattr(self, f'get_{plane}_slice')

    def get_all_planes_by_coords(self, i_sagittal_slice: int, i_coronal_slice: int,
                                 i_horizontal_slice: int, class_idx: int):
        return [self.get_sagittal_slice(i_sagittal_slice, class_idx),
                self.get_coronal_slice(i_coronal_slice, class_idx),
                self.get_horizontal_slice(i_horizontal_slice, class_idx)]

    def get_columndatasources_by_coords(self, i_sagittal_slice: int, i_coronal_slice: int,
                                        i_horizontal_slice: int, class_idx: int):
        slices = self.get_all_planes_by_coords(i_sagittal_slice, i_coronal_slice,
                                               i_horizontal_slice, class_idx)
        slices = [ColumnDataSource(dict(image=[slice])) for slice in slices]
        return dict(zip(self.slice_planes, slices))

    def create_slice_info_div(self, slice: np.ndarray):
        info = self.get_formatted_slice_info(slice)
        return Div(text=self.info_template.format(*info), width=200, height=100)

    def get_slice_info(self, slice: np.ndarray):
        return [getattr(slice, func)() for func in self.info_functions]

    def format_slice_info(self, info: Iterable):
        return [round(value, 2) for value in info]

    def get_formatted_slice_info(self, slice: np.ndarray):
        return self.format_slice_info(self.get_slice_info(slice))

    def get_formatted_slice_info_template(self, slice: np.ndarray):
        return self.info_template.format(*self.get_formatted_slice_info(slice))

    @property
    def n_classes(self):
        return self.image.shape[-1]

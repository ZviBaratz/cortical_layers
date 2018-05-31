import numpy as np

from bokeh.models.widgets import Div
from typing import Iterable


class AllClassAALHandler:
    info_template = '''
    Min: {}<br />
    Max: {}<br />
    Mean: {}<br />
    STD: {}<br />
    '''
    info_functions = {'min', 'max', 'mean', 'std'}

    def __init__(self, image: np.ndarray):
        self.image = image

    def get_sagittal_slice(self, slice: int, cortical_class: int):
        return np.fliplr(np.transpose(self.image[slice, :, :, cortical_class]))

    def get_coronal_slice(self, slice: int, cortical_class: int):
        return self.image[:, slice, :, cortical_class]

    def get_horizontal_slice(self, slice: int, cortical_class: int):
        return np.transpose(self.image[:, :, slice, cortical_class])

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

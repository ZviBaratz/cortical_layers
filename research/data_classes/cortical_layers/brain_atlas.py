import nibabel as nib
import numpy as np


class BrainAtlas:
    _template = None

    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path
        self.region_ids = np.unique(self.template)
        self.n_regions = len(self.region_ids)

    def convert_from_dict(self, value_dict: dict) -> np.ndarray:
        linear_template = self.template.ravel()
        new_array = np.zeros(linear_template.shape)
        if 0 in value_dict:
            keys = [key + 1 for key in value_dict.keys()]
            subtract = True
        else:
            keys = value_dict.keys()
            subtract = False
        for region_id in self.region_ids:
            if region_id in keys:
                key = region_id
                if subtract: key -= 1
                new_array[linear_template == region_id] = value_dict[key]
        return new_array.reshape(self.template.shape)

    @property
    def template(self) -> np.ndarray:
        if not isinstance(self._template, np.ndarray):
            self._template = nib.load(self.path).get_data()
        return self._template

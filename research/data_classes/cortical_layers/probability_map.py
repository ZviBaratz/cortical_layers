import numpy as np

from .brain_atlas import BrainAtlas
from .brain_matrix import BrainMatrix
from .cfg import atlas

class ProbabilityMap(BrainMatrix):
    def __init__(self, data: np.ndarray, class_idx: int, atlas: BrainAtlas = atlas):
        super(ProbabilityMap, self).__init__(data)
        self.class_idx = class_idx
        self.atlas = atlas

    def save(self, path: str) -> None:
        np.save(path, self.data)
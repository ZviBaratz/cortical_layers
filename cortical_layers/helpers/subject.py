import os

from .probability_by_region_matrix import ProbabilityByRegionMatrix


class Subject:
    def __init__(self, name: str, date: str, pbr: ProbabilityByRegionMatrix = None):
        self.name = name
        self.date = date
        self.pbr = pbr
        self.subject_id = name + date
        self.results_dir = os.path.abspath(f'./cortical_layers/results/{self.subject_id}')

    def __eq__(self, other):
        return self.subject_id == other.subject_id

    def save_probability_maps(self):
        self.pbr.save_all_class_probability_maps(self.results_dir)

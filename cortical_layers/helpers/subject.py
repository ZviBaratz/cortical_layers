import os

from .probability_by_region_matrix import ProbabilityByRegionMatrix

results_dir = os.path.abspath('./cortical_layers/results')


class Subject:
    id = None
    pbr = None

    def __init__(self, **kwargs):
        self.set_attributes(**kwargs)
        self.results_dir = os.path.join(results_dir, self.id)

    def set_attributes(self, **kwargs) -> None:
        for key, value in kwargs.items():
            key = key.replace(' ', '_').lower()
            setattr(self, key, value)

    def __eq__(self, other) -> bool:
        return self.id == other.id

    def has_results_dir(self) -> bool:
        return os.path.isdir(self.results_dir)

    def save_probability_maps(self, verbose=False) -> bool:
        if self.pbr:
            if not self.has_results_dir():
                if verbose:
                    print(f'Creating probability maps for subject {self.id}...', end='\t')
                self.pbr.save_all_class_probability_maps(self.results_dir)
                if verbose:
                    print('done!')
                return True
            else:
                if verbose:
                    print(f'Probability maps for subject {self.id} already exist! skipping...')
                return False
        else:
            if verbose:
                print(f'Subject {self.id} has no associated ProbabilityByRegionMatrix instance!')
            return False

    def add_class_probability_by_region_matrix(self, pbr: ProbabilityByRegionMatrix):
        self.pbr = pbr



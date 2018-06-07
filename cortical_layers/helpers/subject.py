import datetime
import os

from .probability_by_region_matrix import ProbabilityByRegionMatrix

results_dir = os.path.abspath('./cortical_layers/results')


class Subject:
    def __init__(self, id: str, name_id: str = None, sex: str = None, date_of_birth: datetime.date = None,
                 dominant_hand: str = None):
        self.id = id
        self.name_id = name_id
        self.sex = sex
        self.date_of_birth = date_of_birth
        self.dominant_hand = dominant_hand
        self.results_dir = os.path.join(results_dir, self.id)

    def __eq__(self, other) -> bool:
        return self.id == other.id

    def has_results_dir(self) -> bool:
        return os.path.isdir(self.results_dir)

    def save_probability_maps(self, verbose=False) -> bool:
        if hasattr(self, 'pbr'):
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
        setattr(self, 'pbr', pbr)

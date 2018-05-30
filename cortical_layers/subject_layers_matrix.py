from scipy.io import loadmat

class SubjectLayersMatrix:
    atlas_regions_axis = 0
    cortical_classes_axis = 1
    n_atlas_regions = 1000
    n_layers = 6
    data_key = 'results'

    def __init__(self, path: str):
        self.path = path
        self.data = self.read_data()

    def read_data(self):
        return loadmat(self.path)[self.data_key]

    def validate_data(self):
        assert self.data.shape[self.atlas_regions_axis] == self.n_atlas_regions
        assert self.data.shape[self.cortical_classes_axis] == self.n_layers

    def get_data(self):
        self.validate_data()
        return self.data
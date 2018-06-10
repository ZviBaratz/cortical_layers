import os

from .brain_atlas import BrainAtlas


n_classes = 6

cortical_layers_data = os.path.normpath(os.path.abspath('./research/data_classes/cortical_layers/data'))
results_dir = os.path.normpath(os.path.abspath('./research/data_classes/cortical_layers/results'))

surface_template_path = os.path.normpath(os.path.abspath('./research/data_classes/cortical_layers/templates/surface_template.nii'))
aal_1000_path = os.path.normpath(os.path.abspath('./research/data_classes/cortical_layers/templates/AAL1000.nii'))
atlas = BrainAtlas(name='AAL', path=aal_1000_path)
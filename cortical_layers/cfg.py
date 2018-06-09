import os
from cortical_layers.helpers.cortical_layers.brain_atlas import BrainAtlas

subjects_data_path = os.path.normpath(os.path.abspath('./cortical_layers/Subjects.xlsx'))
cantab_results_path = os.path.normpath(os.path.abspath('./cortical_layers/RowBySession_Cortical Layers.csv'))

n_classes = 6

cortical_layers_data = os.path.normpath(os.path.abspath('./cortical_layers/data'))
results_dir = os.path.normpath(os.path.abspath('./cortical_layers/results'))

surface_template_path = os.path.normpath(os.path.abspath('./cortical_layers/templates/surface_template.nii'))
aal_1000_path = os.path.normpath(os.path.abspath('./cortical_layers/templates/AAL1000.nii'))
atlas = BrainAtlas(name='AAL', path=aal_1000_path)
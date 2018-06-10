import datetime

from .cantab.cantab_results import CantabResults
from .cortical_layers.probability_by_region_matrix import ProbabilityByRegionMatrix
from .sheets.xlsx_parser.neo_ffi.neo_ffi import NeoFfiResult
from .sheets.xlsx_parser.measurements.subject_measurement import SubjectMeasurements


class Subject:
    _id = None
    _id_length = 9
    additional_data_classes = {
        'measurements': SubjectMeasurements,
        'pbr': ProbabilityByRegionMatrix,
        'cantab': CantabResults,
        'neo_ffi': NeoFfiResult,
    }

    def __init__(self, id: str, name_id: str = None, sex: str = None,
                 date_of_birth: datetime.date = None,
                 dominant_hand: str = None, gender: str = None):
        self.id = id
        self.name_id = name_id
        self.sex = sex
        self.date_of_birth = date_of_birth
        self.dominant_hand = dominant_hand
        self.gender = gender

    def __eq__(self, other) -> bool:
        return self.id == other.id

    def validate_id(self, value: str) -> bool:
        return value.isdigit() and len(value) is self._id_length

    def add_data(self, data_attribute: str, data):
        expected_type = self.additional_data_classes.get(data_attribute)
        if expected_type:
            if isinstance(data, expected_type):
                setattr(self, data_attribute, data)

    def to_dict(self):
        attributes = ('id', 'name_id', 'sex', 'date_of_birth', 'dominant_hand', 'gender')
        return {key: getattr(self, key) for key in attributes}

    def __str__(self):
        return f'{self.name_id}/{self.id}'

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if self.validate_id(value):
            self._id = value
        else:
            raise ValueError(f'Invalid subject ID: {value}!')

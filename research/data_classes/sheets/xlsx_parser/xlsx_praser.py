import os

import pandas as pd

from .neo_ffi.neo_ffi import NeoFfiSheet
from .measurements.measurements import Measurements
from .sheet_parser import SheetParser
from .subjects_attributes import SubjectsAttributes


DEFAULT_PATH = os.path.normpath(os.path.abspath('./research/data_classes/sheets/Subjects.xlsx'))
PARSER = SheetParser()


class XlsxParser:
    _measurements = None
    _neo_ffi = None
    _subjects = None
    _subjects_attributes = None
    sheet_names_dict = {'subject_attributes': 'Subjects',
                        'measurements': 'Measurements',
                        'neo_ffi': 'NEO-FFI'}

    def __init__(self, path: str = DEFAULT_PATH, parser: SheetParser = PARSER):
        self.path = path
        self.parser = parser
        self.update_subjects()

    def get_sheet_data(self, name: str) -> pd.DataFrame:
        return self.parser.parse_sheet(self.path, self.sheet_names_dict[name])

    def get_subject_attributes(self) -> SubjectsAttributes:
        return SubjectsAttributes(self.get_sheet_data('subject_attributes'))

    def get_measurements(self) -> Measurements:
        return Measurements(self.get_sheet_data('measurements'))

    def get_neo_ffi_results(self) -> NeoFfiSheet:
        return NeoFfiSheet(self.get_sheet_data('neo_ffi'))

    def update_subjects(self) -> None:
        for subject in self.subjects:
            measurements = self.measurements.get_subject_measurements(subject.id)
            if measurements is not None:
                subject.add_data('measurements', measurements)

            neo_ffi = self.neo_ffi.get_subject_results(subject.id)
            if neo_ffi is not None:
                subject.add_data('neo_ffi', neo_ffi)

    @property
    def subjects_attributes(self) -> SubjectsAttributes:
        if not isinstance(self._subjects_attributes, SubjectsAttributes):
            self._subjects_attributes = self.get_subject_attributes()
        return self._subjects_attributes

    @property
    def subjects(self) -> list:
        if not isinstance(self._subjects, list):
            self._subjects = self.subjects_attributes.get_subject_instances()
        return self._subjects

    @property
    def measurements(self) -> Measurements:
        if not isinstance(self._measurements, Measurements):
            self._measurements = self.get_measurements()
        return self._measurements

    @property
    def neo_ffi(self):
        if not isinstance(self._neo_ffi, NeoFfiSheet):
            self._neo_ffi = self.get_neo_ffi_results()
        return self._neo_ffi

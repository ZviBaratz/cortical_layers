from .cantab.cantab_results import CantabResults
from .cantab.row_by_session import RowBySessionResults
from .cortical_layers.cortical_layers_results import CorticalLayersResults
from .subject import Subject
from .sheets.xlsx_parser.xlsx_praser import XlsxParser


datasource = XlsxParser()
cortical_layers_results = CorticalLayersResults()
cantab_results = RowBySessionResults()


class DataLoader:
    def __init__(self, subjects: list = datasource.subjects,
                 cortical_layers: CorticalLayersResults = cortical_layers_results,
                 cantab: RowBySessionResults = cantab_results):
        self.subjects = subjects
        self.cortical_layers = cortical_layers
        self.cantab = cantab
        self.add_cortical_layers_results_to_subjects()
        self.add_cantab_results_to_subjects()

    def get_subject_by_id(self, subject_id: str) -> Subject:
        result = [subject for subject in self.subjects if subject.id == subject_id]
        if result:
            return result[0]

    def add_cortical_layers_results_to_subjects(self) -> None:
        for pbr in self.cortical_layers.get_probability_by_region_matrix_instances():
            subject_id = pbr.subject_id
            subject = self.get_subject_by_id(subject_id)
            if isinstance(subject, Subject):
                subject.add_data('pbr', pbr)
            else:
                raise ValueError(f'Invalid subject ID: {subject_id}!')

    def add_cantab_results_to_subjects(self) -> None:
        for subject in self.subjects:
            name_id = subject.name_id
            dob = subject.date_of_birth.strftime('%d/%m/%y')
            results_series = self.cantab.get_subject_results(name_id, dob)
            if isinstance(results_series, CantabResults):
                subject.add_data('cantab', results_series)

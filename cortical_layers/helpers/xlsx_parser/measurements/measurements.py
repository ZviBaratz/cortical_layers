import pandas as pd

from .subject_measurement import SubjectMeasurements


class Measurements:
    date_column_name = 'date'
    subject_id_column_name = 'subject_id'
    measurement_name_column_name = 'measurement'
    _melted = None

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.measurement_columns = self.get_measurement_columns()

    def get_measurement_columns(self):
        measurement_columns = list(self.df.keys())
        measurement_columns.remove(self.date_column_name)
        return measurement_columns

    def melt(self):
        return self.df.reset_index().melt(
            id_vars=[self.subject_id_column_name, self.date_column_name],
            value_vars=[*self.measurement_columns], var_name=self.measurement_name_column_name,
            value_name='value').set_index(self.subject_id_column_name)

    def get_measurement_data(self, measurement_name: str):
        return self.melted.loc[self.melted[self.measurement_name_column_name] == measurement_name]

    def get_subject_data(self, subject_id: str):
        subject_data = self.melted.loc[subject_id].reset_index()
        del subject_data['subject_id']
        subject_data.name = subject_id
        return subject_data

    def get_subject_measurements(self, subject_id: str):
        subject_data = self.get_subject_data(subject_id)
        if not subject_data.empty:
            return SubjectMeasurements(self.get_subject_data(subject_id))
        return None

    @property
    def melted(self):
        if not isinstance(self._melted, pd.DataFrame):
            self._melted = self.melt()
        return self._melted

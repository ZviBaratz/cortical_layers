import pandas as pd


class SubjectMeasurements:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.subject_id = self.df.name

    def get_measurement_data(self, name: str):
        rows = self.df.loc[self.df['measurement'] == name].copy()
        del rows['measurement']
        rows.name = f'{self.subject_id}/{name}'
        return rows

    def get_last_measurement_value(self, name:str):
        return self.get_measurement_data(name)['value'].values[0]

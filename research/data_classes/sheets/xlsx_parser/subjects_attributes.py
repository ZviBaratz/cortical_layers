import pandas as pd

from ...subject import Subject


class SubjectsAttributes:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def create_subject_instance(self, subject_row: tuple) -> Subject:
        subject_id = subject_row[0]
        attributes = subject_row[1]
        return Subject(id=subject_id, **dict(attributes))

    def create_subject_instances(self, df: pd.DataFrame) -> list:
        return [self.create_subject_instance(subject_row) for subject_row in df.iterrows()]

    def get_subject_instances(self):
        return self.create_subject_instances(self.df)

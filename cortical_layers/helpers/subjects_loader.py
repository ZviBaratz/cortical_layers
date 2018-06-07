import pandas as pd

db_path = '/home/flavus/PycharmProjects/cortical_layers/cortical_layers/Subjects.xlsx'


class SubjectsLoader:
    def __init__(self, path: str = db_path):
        self.path = path
        self.df = self.read_subjects_db()

    def read_subjects_db(self):
        return pd.read_excel(self.path, sheet_name='Subjects', index_col=0)

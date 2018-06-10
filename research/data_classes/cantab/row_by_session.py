import os
import glob

import pandas as pd

from .cantab_results import CantabResults

DEFAULT_PATH = glob.glob('./research/data_classes/cantab/RowBySession_*.csv')
if DEFAULT_PATH:
    DEFAULT_PATH = DEFAULT_PATH[0]
cantab_df = pd.read_csv(DEFAULT_PATH)


class RowBySessionResults:
    def __init__(self, df: pd.DataFrame = cantab_df):
        self.df = df

    def get_subject_by_name_id(self, name_id: str):
        return self.df.loc[self.df['Subject ID'].map(str.lower) == name_id.lower()]

    def get_subject_by_dob(self, dob: str):
        return self.df.loc[self.df['Date of birth'] == dob]

    def get_subject_series(self, name_id: str, dob: str):
        by_name = self.get_subject_by_name_id(name_id)
        if len(by_name) is 0:
            by_dob = self.get_subject_by_dob(dob)
            if len(by_dob) is 0:
                return None
            elif len(by_dob) > 1:
                return None
            else:
                return by_dob.squeeze()
        elif len(by_name) > 1:
            return None
        else:
            return by_name.squeeze()

    def get_subject_results(self, name_id: str, dob: str):
        return CantabResults(self.get_subject_series(name_id, dob))

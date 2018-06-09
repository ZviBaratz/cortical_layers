import pandas as pd

from .neo_ffi_result import NeoFfiResult


class NeoFfiSheet:
    def __init__(self, df: pd.DataFrame):
        self.df = df.dropna()

    def get_subject_results(self, subject_id: str):
        try:
            return NeoFfiResult(self.df.loc[subject_id])
        except KeyError:
            return None
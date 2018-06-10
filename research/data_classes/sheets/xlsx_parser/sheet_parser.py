import pandas as pd

LEN_SUBJECT_ID = 9

class SheetParser:
    def __init__(self):
        pass

    def read_from_path(self, path: str, sheet_name: str):
        return pd.read_excel(path, sheet_name=sheet_name, index_col=0)

    def fix_column_name(self, name: str):
        return name.replace(' ', '_').replace("'", '').lower()

    def create_fixed_column_names_dict(self, column_names: pd.Index):
        return {name: self.fix_column_name(name) for name in column_names}

    def fix_column_names(self, df: pd.DataFrame):
        fixed_names_dict = self.create_fixed_column_names_dict(df.columns)
        return df.rename(columns=fixed_names_dict)

    def fix_index_names(self, df: pd.DataFrame):
        return [self.fix_column_name(name) for name in df.index.names]

    def fix_index(self, value):
        return str(value).zfill(LEN_SUBJECT_ID)

    def fix_index_values(self, df: pd.DataFrame):
        return df.index.map(self.fix_index)

    def parse_sheet(self, path: str, sheet_name: str):
        raw_df = self.read_from_path(path, sheet_name)
        raw_df.index.names = self.fix_index_names(raw_df)
        raw_df.index = self.fix_index_values(raw_df)
        return self.fix_column_names(raw_df)

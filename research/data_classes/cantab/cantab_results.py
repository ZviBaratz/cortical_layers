import pandas as pd


class CantabResults:
    def __init__(self, series: pd.Series):
        self.series = series

    def get_measure(self, name: str):
        return self.series[name]

    def get_task_meaures(self, task_name: str):
        return {name: score for name, score in self.series.to_dict().items() if
                name.startswith(task_name) and ' ' not in name}

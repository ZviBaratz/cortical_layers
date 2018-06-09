import pandas as pd


class NeoFfiResult:
    big_five = ('neuroticism', 'extraversion', 'openness', 'agreeableness', 'conscientiousness')

    def __init__(self, series: pd.Series):
        self.series = series
        for attribute in self.big_five:
            setattr(self, attribute, self.series[attribute])
from pytest import fixture
from pandas import DataFrame


@fixture
def dataframe() -> DataFrame:
    return DataFrame({
        'a': ['a', 'a', 'a', 'a', 'b', 'b', 'b', 'b'],
        'b': ['0', '0', '1', '1', '0', '0', '1', '1'],
        'm': [0, 1, 2, 3, 4, 5, 6, 7],
        'n': [10] * 8,
    })

from typing import List
from pandas import DataFrame, Index, MultiIndex
from pytest import fixture, mark

from simple_pivot.pivot import Config, Pivot


@fixture
def dataframe() -> DataFrame:
    return DataFrame({
        "a": ["a", "a", "a", "a", "b", "b", "b", "b"],
        "b": ["0", "0", "1", "1", "0", "0", "1", "1"],
        "c": ["y", "y", "y", "x", "x", "x", "x", "x"],
        "d": ["_", "_", "_", "_", "_", "^", "^", "^"],
        "m": list(range(8)),
        "n": [10] * 8,
    })


@fixture
def pivot(dataframe) -> Pivot:
    pivot = Pivot(Config(
        rows="a",
        cols="b",
        vals=["m", "n"]
    ))
    pivot._data = dataframe
    return pivot


def test_agg_computable_expression(dataframe: DataFrame, pivot: Pivot):
    def exp(m, n):
        return m / n

    expected = DataFrame({
        "a": ["a", "a", "b", "b"],
        "b": ["0", "1", "0", "1"],
        "exp": [0.05, 0.25, 0.45, 0.65],
    }, index=[0, 1, 2, 3])

    actual = pivot._agg_computable_expression(dataframe, exp, ["a", "b"])
    assert actual.equals(expected)


@mark.parametrize(
    "rows, cols, expected", [
        (
            ["a"],
            ["b"],
            DataFrame(
                [
                    [1.0, 5.0, 6],
                    [9.0, 13.0, 22],
                    [10.0, 18.0, 28],
                ],
                index=Index(["a", "b", "Total"], name="a"),
                columns=MultiIndex.from_tuples([
                    ("", "m", "0"),
                    ("", "m", "1"),
                    ("Total", "m", ""),
                ], name=["", "Values", ""]),
            ),
        ),
        (
            ["a", "b"],
            None,
            DataFrame(
                {"m": [1.0, 5.0, 9.0, 13.0, 28.0]},
                index=MultiIndex.from_tuples([
                    ("a", "0"),
                    ("a", "1"),
                    ("b", "0"),
                    ("b", "1"),
                    ("Total", ""),
                ], names=["a", "b"]),
                columns=Index(["m"], name="Values"),
            ),
        ),
    ]
)
def test_make_pivot(
    rows: List[str],
    cols: List[str],
    expected: DataFrame,
    dataframe: DataFrame,
    pivot: Pivot
):
    pivot._data = dataframe
    pivot._config._rows = rows
    pivot._config._cols = cols
    pivot._config._vals = ["m"]
    actual = pivot._make_pivot()
    assert actual.equals(expected)

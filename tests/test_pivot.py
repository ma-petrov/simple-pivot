from typing import List
from pandas import DataFrame, Index, MultiIndex
from pytest import fixture, mark
from simple_pivot.agg_val import AggVal

from simple_pivot.pivot import Config, Pivot


@fixture
def dataframe() -> DataFrame:
    return DataFrame({
        "a": ["a", "a", "a", "a", "b", "b", "b", "b"],
        "b": ["0", "0", "1", "1", "0", "0", "1", "1"],
        "c": ["y", "y", "y", "x", "x", "x", "x", "x"],
        "d": ["_", "_", "_", "_", "_", "^", "^", "^"],
        "m": [float(i) for i in range(8)],
        "n": [10.0] * 8,
    })


@fixture
def seasons() -> DataFrame:
    return DataFrame({
        'season': ['summer'] * 10 + ['winter'] * 10,
        'month': ['Jul'] * 5 + ['Aug'] * 5 + ['Jan'] * 5 + ['Feb'] * 5,
        'v': [float(i) for i in range(20)],
        'd': [50.0] * 20,
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


def expression(m, n):
    return m / n


@mark.parametrize(
    "by, vals, expected", [
        (
            None,
            [AggVal("m"), AggVal("n"), AggVal(expression)],
            DataFrame({
                "sum of m": [28.0],
                "sum of n": [80.0],
                "expression": [0.35],
            }, index=Index(["Total"], name="Total")),
        ),
        (
            None,
            [
                AggVal("m"),
                AggVal("n"),
                AggVal("m", agg_func="mean"),
                AggVal("m", agg_func="mean", name="AVERAGE DUE"),
                AggVal(expression),
            ],
            DataFrame({
                "sum of m": [28.0],
                "sum of n": [80.0],
                "mean of m": [3.5],
                "AVERAGE DUE": [3.5],
                "expression": [0.35],
            }, index=Index(["Total"], name="Total")),
        ),
        (
            "a",
            [AggVal("m"), AggVal("n"), AggVal(expression)],
            DataFrame({
                "sum of m": [6.0, 22.0],
                "sum of n": [40.0, 40.0],
                "expression": [0.15, 0.55],
            }, index=Index(["a", "b"], name="a")),
        ),
        (
            "a",
            [
                AggVal("m"),
                AggVal("n"),
                AggVal("m", agg_func="mean"),
                AggVal("m", agg_func="mean", name="AVERAGE DUE"),
                AggVal(expression),
            ],
            DataFrame({
                "sum of m": [6.0, 22.0],
                "sum of n": [40.0, 40.0],
                "mean of m": [1.5, 5.5],
                "AVERAGE DUE": [1.5, 5.5],
                "expression": [0.15, 0.55],
            }, index=Index(["a", "b"], name="a")),
        ),
        (
            ["a", "b"],
            [AggVal("m"), AggVal("n"), AggVal(expression)],
            DataFrame(
                {
                    "sum of m": [1.0, 5.0, 9.0, 13.0],
                    "sum of n": [20.0, 20.0, 20.0, 20.0],
                    "expression": [0.05, 0.25, 0.45, 0.65],
                },
                index=MultiIndex.from_tuples(
                    [("a", "0"), ("a", "1"), ("b", "0"), ("b", "1")],
                    name=("a", "b"),
                ),
            ),
        ),
    ]
)
def test_aggregate(
    dataframe: DataFrame,
    by: List[str],
    vals: List[AggVal],
    expected: DataFrame,
):    
    pivot = Pivot(Config(rows=[], vals=vals))
    actual = pivot._aggregate(dataframe, by=by)
    assert actual.equals(expected)


@mark.parametrize(
    "rows, cols, vals, expected", [
        (
            ["a"],
            ["b"],
            [AggVal("m")],
            DataFrame(
                [
                    [1.0, 5.0, 6.0],
                    [9.0, 13.0, 22.0],
                    [10.0, 18.0, 28.0],
                ],
                index=Index(["a", "b", "Total"], name="a"),
                columns=MultiIndex.from_tuples([
                    ("", "sum of m", "0"),
                    ("", "sum of m", "1"),
                    ("Total", "sum of m", ""),
                ]),
            ),
        ),
        (
            ["a", "b"],
            None,
            [AggVal("m")],
            DataFrame(
                {"sum of m": [1.0, 5.0, 9.0, 13.0, 28.0]},
                index=MultiIndex.from_tuples([
                    ("a", "0"),
                    ("a", "1"),
                    ("b", "0"),
                    ("b", "1"),
                    ("Total", ""),
                ], names=["a", "b"]),
                columns=Index(["sum of m"]),
            ),
        ),
        (
            ["a"],
            None,
            [AggVal("m")],
            DataFrame(
                {"sum of m": [6.0, 22.0, 28.0]},
                index=Index(["a", "b", "Total"], name="a"),
                columns=Index(["sum of m"]),
            ),
        ),
        (
            ["a"],
            None,
            [AggVal(lambda m, n: m/n, name="ratio")],
            DataFrame(
                [[0.15], [0.55], [0.35]],
                index=Index(["a", "b", "Total"], name="a"),
                columns=Index(["ratio"]),
            ),
        ),
    ]
)
def test_make_pivot(
    rows: List[str],
    cols: List[str],
    vals: List[str],
    expected: DataFrame,
    dataframe: DataFrame,
    pivot: Pivot
):
    pivot._data = dataframe
    pivot._config._rows = rows
    pivot._config._cols = cols
    pivot._config._vals = vals
    actual = pivot._make_pivot()
    assert actual.equals(expected)


@mark.skip()
def test_make_pivot_2(seasons: DataFrame):
    expected = DataFrame(
        {"sum of v": [45.0, 145.0, 190.0], "sum of d": [45.0, 145.0, 190.0]},
        index=Index(["summer", "winter", "Total"], name="season"),
        columns=Index(["v"], name="Values"),
    )

    pivot = Pivot(
        Config(
            vals=[AggVal("v"), AggVal("d")],
            rows=["season"],
            cols=["month"],
        ),
        source=seasons,
    )

    actual = pivot.show()
    assert actual.equals(expected)

from typing import List
from pandas import DataFrame, Index, MultiIndex
from pytest import fixture, mark

from simple_pivot.config import AggVal
from simple_pivot.pivot import Pivot


@fixture
def dataframe() -> DataFrame:
    return DataFrame(
        {
            "a": ["a", "a", "a", "a", "b", "b", "b", "b"],
            "b": ["0", "0", "1", "1", "0", "0", "1", "1"],
            "c": ["y", "y", "y", "x", "x", "x", "x", "x"],
            "d": ["_", "_", "_", "_", "_", "^", "^", "^"],
            "m": [float(i) for i in range(8)],
            "n": [10.0] * 8,
        }
    )


@fixture
def pivot(dataframe) -> Pivot:
    return Pivot(
        config={"rows": "a", "cols": "b", "vals": ["m", "n"]}, source=dataframe
    )


def expression(m, n):
    return m / n


@mark.parametrize(
    "by, vals, expected",
    [
        (
            None,
            [AggVal(val="m"), AggVal(val="n"), AggVal(val=expression)],
            DataFrame(
                {"sum of m": [28.0], "sum of n": [80.0], "expression": [0.35]},
                index=Index(["Total"], name="Total"),
            ),
        ),
        (
            None,
            [
                AggVal(val="m"),
                AggVal(val="n"),
                AggVal(val="m", agg_func="mean"),
                AggVal(val="m", agg_func="mean", name="AVERAGE DUE"),
                AggVal(val=expression),
            ],
            DataFrame(
                {
                    "sum of m": [28.0],
                    "sum of n": [80.0],
                    "mean of m": [3.5],
                    "AVERAGE DUE": [3.5],
                    "expression": [0.35],
                },
                index=Index(["Total"], name="Total"),
            ),
        ),
        (
            "a",
            [AggVal(val="m"), AggVal(val="n"), AggVal(val=expression)],
            DataFrame(
                {
                    "sum of m": [6.0, 22.0],
                    "sum of n": [40.0, 40.0],
                    "expression": [0.15, 0.55],
                },
                index=Index(["a", "b"], name="a"),
            ),
        ),
        (
            "a",
            [
                AggVal(val="m"),
                AggVal(val="n"),
                AggVal(val="m", agg_func="mean"),
                AggVal(val="m", agg_func="mean", name="AVERAGE DUE"),
                AggVal(val=expression),
            ],
            DataFrame(
                {
                    "sum of m": [6.0, 22.0],
                    "sum of n": [40.0, 40.0],
                    "mean of m": [1.5, 5.5],
                    "AVERAGE DUE": [1.5, 5.5],
                    "expression": [0.15, 0.55],
                },
                index=Index(["a", "b"], name="a"),
            ),
        ),
        (
            ["a", "b"],
            [AggVal(val="m"), AggVal(val="n"), AggVal(val=expression)],
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
    ],
)
def test_aggregate(
    dataframe: DataFrame, by: List[str], vals: List[AggVal], expected: DataFrame
):
    pivot = Pivot(config={"rows": [], "vals": vals})
    actual = pivot._aggregate(dataframe, by=by)
    assert actual.equals(expected)


@mark.parametrize(
    "config, expected",
    [
        (
            {"vals": "m", "rows": "a", "cols": "b"},
            DataFrame(
                [[1.0, 5.0, 6.0], [9.0, 13.0, 22.0], [10.0, 18.0, 28.0]],
                index=Index(["a", "b", "Total"], name="a"),
                columns=MultiIndex.from_tuples(
                    [
                        ("", "sum of m", "0"),
                        ("", "sum of m", "1"),
                        ("Total", "sum of m", ""),
                    ]
                ),
            ),
        ),
        (
            {"vals": "m", "rows": ["a", "b"]},
            DataFrame(
                {"sum of m": [1.0, 5.0, 9.0, 13.0, 28.0]},
                index=MultiIndex.from_tuples(
                    [
                        ("a", "0"),
                        ("a", "1"),
                        ("b", "0"),
                        ("b", "1"),
                        ("Total", ""),
                    ],
                    names=["a", "b"],
                ),
                columns=Index(["sum of m"]),
            ),
        ),
        (
            {"vals": "m", "rows": ["a"]},
            DataFrame(
                {"sum of m": [6.0, 22.0, 28.0]},
                index=Index(["a", "b", "Total"], name="a"),
                columns=Index(["sum of m"]),
            ),
        ),
        (
            {"vals": {"val": lambda m, n: m / n, "name": "ratio"}, "rows": "a"},
            DataFrame(
                [[0.15], [0.55], [0.35]],
                index=Index(["a", "b", "Total"], name="a"),
                columns=Index(["ratio"]),
            ),
        ),
    ],
)
def test_make_pivot(config: dict, expected: DataFrame, dataframe: DataFrame):
    pivot = Pivot(config=config, source=dataframe)

    actual = pivot._make_pivot()
    assert actual.equals(expected)

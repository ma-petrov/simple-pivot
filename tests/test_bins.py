from collections.abc import Iterable
from typing import Any
from pytest import fixture, mark
from pandas import DataFrame

from simple_pivot.bins import make_bins_by_agg_col, search_bin_index


@fixture
def dataframe() -> DataFrame:
    return DataFrame(
        {
            "b": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            "a": [0, 0, 0, 0, 1, 9, 1, 1, 9, 1],
        }
    )


def f(l: Iterable, i: int) -> Any:
    return sum(l[: i + 1])


@mark.parametrize(
    "l, f, target, expected",
    [
        ([0, 1, 2, 3, 4], f, 6, 3),  # сумму 6 дают элементы с 0 по 3
        ([0, 1, 2, 3, 4], f, 5, 3),  # приближенное равенство даст 2 элемент
    ],
)
def test_search_bin_index(l, f, target, expected):
    assert search_bin_index(l, f, target) == expected


def test_make_bins_by_agg_col(dataframe):
    """Проверка корректности разбиения на бины.

    Для удобства чтения в фикстуре dataframe колонка "b" уже отсортирована.
    Видно, что чтобы сумма колонки "a" распределилась равномерно, нужно взять
    строки 0 - 6 для первого бина и строки 7 - 9 для второго. Поэтому граница
    определяется как 6."""
    assert make_bins_by_agg_col(dataframe, "b", "a", 2) == [6]

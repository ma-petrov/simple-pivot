from typing import Any

from pytest import fixture 
from pandas import DataFrame

from simple_pivot.main import agg_computable_expression


def expression(a: Any, b: Any) -> int:
    return a / b


@fixture
def data() -> DataFrame:
    return DataFrame({
        'a': [1, 1, 3, 3],
        'b': [4, 4, 4, 4],
    })


def test_agg_computable_expression(data):
    """Проверяет корректность работы вычислимого выражения.

    Сумма столбца "a" датафрейма - 8, столбца "b" - 16. Ожидаемый результат
    функции - 0.5.
    """
    assert agg_computable_expression(data, expression, sum) == 0.5

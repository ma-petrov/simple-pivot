from typing import Callable
from pytest import fixture

from simple_pivot.agg_val import AggVal


@fixture
def expression() -> Callable:
    def past_due_ratio(past_due: float, outstanding: float) -> float:
        return past_due / outstanding
    return past_due_ratio


def test_init__str_col():
    agg_val = AggVal("outstanding")
    assert agg_val.val == "outstanding"
    assert agg_val.agg_func == "sum"
    assert agg_val.name == "sum of outstanding"


def test_init__str_col__agg_func_passed():
    agg_val = AggVal("outstanding", agg_func="mean")
    assert agg_val.val == "outstanding"
    assert agg_val.agg_func == "mean"
    assert agg_val.name == "mean of outstanding"


def test_init__str_col__name_passed():
    agg_val = AggVal("outstanding", name="SUM(out)")
    assert agg_val.val == "outstanding"
    assert agg_val.agg_func == "sum"
    assert agg_val.name == "SUM(out)"


def test_init__str_col__agg_func_name_passed():
    agg_val = AggVal("outstanding", agg_func="mean", name="MEAN(out)")
    assert agg_val.val == "outstanding"
    assert agg_val.agg_func == "mean"
    assert agg_val.name == "MEAN(out)"


def test_init__expression_col(expression: Callable):
    agg_val = AggVal(expression)
    assert agg_val.val == expression
    assert agg_val.agg_func == "sum"
    assert agg_val.name == "past_due_ratio"
    assert agg_val.val(5, 100) == 0.05


def test_init__expression_col__agg_func_passed(expression: Callable):
    agg_val = AggVal(expression, agg_func="mean")
    assert agg_val.val == expression
    assert agg_val.agg_func == "mean"
    assert agg_val.name == "past_due_ratio"
    assert agg_val.val(5, 100) == 0.05


def test_init__expression_col__name_passed(expression: Callable):
    agg_val = AggVal(expression, name="SUM(Past Due Ratio)")
    assert agg_val.val == expression
    assert agg_val.agg_func == "sum"
    assert agg_val.name == "SUM(Past Due Ratio)"
    assert agg_val.val(5, 100) == 0.05


def test_init__expression_col__agg_func_name_passed(expression: Callable):
    agg_val = AggVal(expression, agg_func="mean", name="MEAN(Past Due Ratio)")
    assert agg_val.val == expression
    assert agg_val.agg_func == "mean"
    assert agg_val.name == "MEAN(Past Due Ratio)"
    assert agg_val.val(5, 100) == 0.05


def test_get_cols_to_aggregate__str_col():
    agg_val = AggVal("outstanding")
    assert agg_val.get_cols_to_aggregate() == {'outstanding': 'sum'}


def test_get_cols_to_aggregate__expression_col(expression):
    agg_val = AggVal(expression)
    assert agg_val.get_cols_to_aggregate() == {
        "past_due": "sum",
        "outstanding": "sum",
    }

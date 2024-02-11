from __future__ import annotations

from typing import Any, Callable, List, Union
from pandas import DataFrame

from pydantic import BaseModel, model_validator
from simple_pivot.exceptions import MissingConfigKeyError


FORBID = "forbid"
AFTER = "after"


def default_formatting(x: float) -> float:
    return round(x, 2)


class AggVal(BaseModel, extra=FORBID):
    val: Union[str, Callable]
    agg_func: str = "sum"
    name: str = None
    formatting: Callable = default_formatting

    @model_validator(mode=AFTER)
    def set_name(self) -> AggVal:
        self.name = self.name or self._get_name()
        return self

    @property
    def is_computable_expression(self) -> bool:
        return isinstance(self.val, Callable)

    @property
    def expression_arg_names(self) -> List[str]:
        if self.is_computable_expression:
            return list(self.val.__code__.co_varnames)

    def compute(self, dataframe: DataFrame) -> DataFrame:
        return dataframe.apply(lambda x: self.val(*x.values), axis=1)

    def get_cols_to_aggregate(self) -> dict[str, str]:
        if self.is_computable_expression:
            return {k: self.agg_func for k in self.expression_arg_names}
        else:
            return {self.val: self.agg_func}

    def _get_name(self) -> str:
        if self.is_computable_expression:
            return self.val.__name__
        else:
            return f"{self.agg_func} of {self.val}"


class Config(BaseModel, extra=FORBID):
    vals: Union[str, Callable, AggVal, List[Union[str, Callable, AggVal]]]
    rows: Union[str, List[str]] = None
    cols: Union[str, List[str]] = None

    @model_validator(mode=AFTER)
    def fields_to_list(self) -> Config:
        if self.rows is None and self.cols is None:
            raise MissingConfigKeyError(
                "Нужно передать хотя бы один из параметров rows, cols."
            )

        for attr in ("vals", "rows", "cols"):
            setattr(self, attr, self._to_list(getattr(self, attr)))

        # TODO костыль для случая, когда вместо словаря в vals передана строка
        # или функция. Подумать, возможно ли сделать через pydantic.
        for i, val in enumerate(self.vals):
            if isinstance(val, (str, Callable)):
                self.vals[i] = AggVal(val=val)

        return self

    def _to_list(self, x: Any) -> List:
        if x is not None:
            return [*x] if isinstance(x, (tuple, list)) else [x]

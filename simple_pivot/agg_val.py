from typing import Callable, List, Optional, Tuple, Union

from pandas import DataFrame


class AggVal:
    def __init__(
        self,
        val: Union[str, Callable],
        agg_func: Optional[str] = None,
        name: Optional[str] = None,
    ):
        self.val = val
        self.agg_func = agg_func or "sum"
        self.name = name or self._get_name()
    
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


class CompulableExpressionAggregation:
    def __init__(
        self,
        val: Union[str, Callable],
        agg_func: Optional[str] = None,
        name: Optional[str] = None,
    ):
        self.val = val
        self.agg_func = agg_func or "sum"
        self.name = name or self._get_name()
    
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

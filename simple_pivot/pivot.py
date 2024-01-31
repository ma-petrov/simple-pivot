from typing import Callable, List, Optional, Union
from pandas import DataFrame, MultiIndex, concat


from simple_pivot.source import BaseSource


class Config:
    def __init__(
        self,
        rows: Union[str, List[str]],
        vals: Union[str, List[str]],
        cols: Optional[Union[str, List[str]]] = None,
        agg_func: Optional[str] = None,
    ):
        self._rows = rows if isinstance(rows, List) else [rows]
        self._vals = vals if isinstance(vals, List) else [vals]
        
        self._cols = None
        if cols:
            self._cols = cols if isinstance(cols, List) else [cols]
        
        self._agg_func = agg_func or 'sum'


class Pivot:
    TOTAL = "Total"
    VALUES = "Values"

    def __init__(
        self,
        config: Config,
        source: Optional[DataFrame] = None,
    ):
        self._config = config
        self._data = source

    def set_source(self, source: DataFrame) -> None:
        self._data = source

    def show(self) -> DataFrame:
        """Вычисляет и отображает сводную таблицу.
        
        :return: html объект с отображением сводной таблицы
        """
        return self._make_pivot()

    def _agg_computable_expression(
        self,
        dataframe: DataFrame,
        exp: Callable,
        by: Optional[Union[str, List[str]]] = None,
        agg_func: Optional[str] = None,
    ) -> DataFrame:
        """Аггрегирует несколько колонок в одно значение.
        
        Вычистляет аггрегированные значения нескольких столбцов, затем применяет их
        рузультаты в функции expression. Названия аргументов функции соответствуют
        названиям столбцов.

        :param data: dataframe.
        :param expression: функция вычислимого выражения.
        :param agg_func: функция аггрегации, применяющаяся отдельно для каждого
        столбца.

        :return: результат аггрегации. 
        """
        name = exp.__name__
        agg_func = agg_func or "sum"
        col_names = exp.__code__.co_varnames

        if by is None:
            aggregated = dataframe.aggregate({c: agg_func for c in col_names})
        else:
            aggregated = (
                dataframe
                .groupby(by)
                .aggregate({c: agg_func for c in col_names})
            )

        aggregated[name] = aggregated.apply(lambda r: exp(*r.values), axis=1)
        return aggregated.reset_index()[by + [name]]
    
    def _agg_val(
        self,
        dataframe: DataFrame,
        val: List[Union[str, Callable]],
        by: Optional[Union[str, List[str]]] = None,
        agg_func: Optional[str] = None,
    ) -> DataFrame:
        """Возвращает аггрегаты"""
        if isinstance(val, Callable):
            aggregated = self._agg_computable_expression(
                dataframe, val, by, agg_func
            )
        else:
            if by is None:
                aggregated = dataframe.aggregate({val: agg_func})
            else:
                aggregated = (
                    dataframe
                    .groupby(by, as_index=False)
                    .aggregate({val: agg_func})
                )
        return aggregated
    
    def _set_top_column(self, dataframe: DataFrame, top_name: str) -> None:
        name = dataframe.columns.name
        name = [name] if isinstance(name, str) else name
        names = ["", self.VALUES] + name
        columns = [("", top_name, c) for c in dataframe.columns]
        dataframe.columns = MultiIndex.from_tuples(columns, names=names)

    def _total_index(self, rows: List[str]) -> tuple[str]:
        sapces = [""] * (len(rows) - 1)
        return (self.TOTAL, *sapces)

    def _concat_agg_vals_and_cols_totals(
        self,
        rows: List[str],
        cols: List[str],
        val: str,
        agg_vals: DataFrame,
        agg_row_totals: DataFrame,
    ) -> DataFrame:
        total = agg_row_totals.set_index(cols).T
        pivot = agg_vals.pivot(index=rows, columns=cols, values=val)
        pivot.loc[self._total_index(rows)] = total.loc[val]
        self._set_top_column(pivot, val)
        return pivot

    def _make_pivot(self) -> DataFrame:
        rows = self._config._rows
        cols = self._config._cols
        vals = self._config._vals
        agg_func = self._config._agg_func

        pivot_segments = []

        for val in vals:
            by = rows + cols if cols else rows
            agg_vals = self._agg_val(
                self._data, val, by=by, agg_func=agg_func
            )
            agg_col_totals = self._agg_val(
                self._data, val, by=cols, agg_func=agg_func
            )
            val_name = val.__name__ if isinstance(val, Callable) else val

            if cols:
                pivot_segment = self._concat_agg_vals_and_cols_totals(
                    rows, cols, val_name, agg_vals, agg_col_totals
                )
            else:
                total = agg_col_totals[val_name]
                pivot_segment = agg_vals.set_index(rows)
                pivot_segment.columns.name = self.VALUES
                pivot_segment.loc[self._total_index(rows), val_name] = total
            pivot_segments.append(pivot_segment)

        if cols:
            for val in vals:
                val_name = val.__name__ if isinstance(val, Callable) else val
                total = self._agg_val(self._data, val, by=rows, agg_func=agg_func)
                total.set_index(rows, inplace=True)
                total.loc[self.TOTAL] = self._agg_val(
                    self._data, val, agg_func=agg_func
                )
                dump = ["" for _ in range(len(cols))]
                total.columns = MultiIndex.from_tuples(
                    [("Total", val, *dump)],
                    names=["", "Values", *dump]
                )
                pivot_segments.append(total)

        return concat(pivot_segments, axis=1)

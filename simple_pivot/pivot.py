from typing import Dict, List, Optional, Union
from pandas import DataFrame, Index, MultiIndex, concat, melt

from simple_pivot.agg_val import AggVal


class Config:
    IN_COLS = "IN_COLS"
    IN_ROWS = "IN_ROWS"

    def __init__(
        self,
        vals: List[AggVal],
        rows: Optional[Union[str, List[str]]] = None,
        cols: Optional[Union[str, List[str]]] = None,
        vals_position: Optional[str] = None,
    ):
        if rows is None and cols is None:
            raise ValueError('At least on of rows of cols must be passed.')

        self._rows = None
        if rows:
            self._rows = rows if isinstance(rows, List) else [rows]
        
        self._cols = None
        if cols:
            self._cols = cols if isinstance(cols, List) else [cols]

        self._vals = vals
        self._vals_position = vals_position or self.IN_COLS


class Pivot:
    TOTAL = "Total"
    VALUES = "Values"

    INDEX = "index"
    COLUMNS = "columns"

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
    
    def _agg_dict(self) -> Dict[str, List[str]]:
        """Собирает словарь со всеми аггрегируемыми колонками и функциями."""
        agg = {}
        for val in self._config._vals:
            for col, agg_func in val.get_cols_to_aggregate().items():
                agg[col] = agg.get(col, set()) | {agg_func}
        return {k: list(v) for k, v in agg.items()}
    
    def _append_index_level(
        self,
        dataframe: DataFrame,
        index_name: str,
        level_name: Optional[str] = None,
        axis: Optional[str] = None,
    ) -> DataFrame:
        level_name = level_name or ""
        axis = axis or self.INDEX
        
        index: Union[Index, MultiIndex] = getattr(dataframe, axis)

        if isinstance(index, MultiIndex):
            columns = [(index_name, *c) for c in index]
            names = (level_name, *index.names)
        else:
            columns = [(index_name, c) for c in index]
            names = (level_name, index.name)

        appended_index = MultiIndex.from_tuples(columns, names=names)
        setattr(dataframe, axis, appended_index)
        return dataframe

    def _aggregate(
        self,
        dataframe: DataFrame,
        by: Optional[Union[str, List[str]]] = None,
        values_axis: Optional[str] = None,
    ) -> DataFrame:
        """"""
        values_axis = values_axis or self.COLUMNS
        agg = self._agg_dict()

        # Если не нужно группировать, создается фиктивная колонка Total с
        # одинаковым значением.
        if not by:
            by = self.TOTAL
            dataframe[self.TOTAL] = [self.TOTAL] * dataframe.shape[0]

        # Сборка результирующих аггрегатов, для простых - копирование колонок,
        # для вычислимых выражений применяется apply.
        aggregated = dataframe.groupby(by).agg(agg)
        result = DataFrame()

        for val in self._config._vals:
            if val.is_computable_expression:
                cols = [(c, val.agg_func) for c in val.expression_arg_names]
                result[val.name] = val.compute(aggregated[cols])
            else:
                result[val.name] = aggregated[(val.val, val.agg_func)]

        return result        

    def _merge(self, values: DataFrame, totals: DataFrame) -> DataFrame:
        columns = [("", *c) for c in values.columns]
        names = ("", *values.columns.names)
        values.columns = MultiIndex.from_tuples(columns, names=names)

        dump = [""] * (len(values.columns.names) - 2)
        totals.columns = [(self.TOTAL, c, *dump) for c in totals.columns]

        return concat([values, totals], axis=1)
    
    def _concat(self, values: DataFrame, totals: DataFrame) -> DataFrame:
        if dump := [""] * (len(values.index.names) - 1):
            totals.index = MultiIndex.from_tuples(
                [(self.TOTAL, *dump)],
                name=values.index.names
            )
        return concat([values, totals])
    
    def _melt(
        self,
        dataframe: DataFrame,
        cols: List[str],
        index: Optional[str] = None
    ) -> DataFrame:
        index = index or self.VALUES
        dataframe[index] = [index] * dataframe.shape[0]
        dataframe = dataframe.reset_index().pivot(
            index=index,
            columns=cols,
            values=[v.name for v in self._config._vals],
        )
        dataframe.index.name = None
        return dataframe

    def _make_pivot(self) -> DataFrame:
        rows = self._config._rows
        cols = self._config._cols
        
        values = self._aggregate(self._data, by=(rows or []) + (cols or []))
        totals = self._aggregate(self._data)

        # Заданы столбцы
        if cols is None:
            return self._concat(values, totals)

        # Заданы строки
        if rows is None:
            values = self._melt(values, cols)
            totals.index = [self.VALUES]
            return self._merge(values, totals)
        
        # Заданы столбцы и строки
        row_totals = self._aggregate(self._data, by=rows)
        col_totals = self._aggregate(self._data, by=cols)
        col_totals = self._melt(col_totals, cols, index=self.TOTAL)
        values = values.reset_index().pivot(
            index=rows,
            columns=cols,
            values=[v.name for v in self._config._vals]
        )
        
        return self._concat(
            self._merge(values, row_totals),
            self._merge(col_totals, totals),
        )

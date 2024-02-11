from typing import Dict, List, Optional, Union
from pandas import DataFrame, MultiIndex, concat
from pandas.io.formats.style import Styler

from simple_pivot.utils import parse_styles
from simple_pivot.config import Config


class Pivot:
    """Класс сводной таблицы.
    
    Для конфигурации используются словарь, содержащий следующие ключи:
        
    1. vals - определяет, данные каких столбцов нужно аггрегировать. Может быть
    строкой, функцией или словарем, если нужно задать один столбец. Также может
    быть списокм или кортежем, элементы которых будут могут быть строкой, функ-
    цией или словарем, если требуется задать несколько столбцов для аггрегации.

    2. rows - строка или список строк с названиями столбцов, в разрезе которых
    данные будут аггрегированы по строкам сводной таблицы.

    3. cols - аналогично rows, но разрезы по столбцам сводной таблицы.
    
    Пример словаря с конфигурацией:
    .. code-block:: python
    {
        "vals": [
            "count",
            {
                "val": "price",
            },
            {
                "val": lambda price, count: price/count,
                "agg_func": "mean",
                "name": "Average price of item",
                "formatting": lambda x: round(x, 3),
            },
        ],
        "rows": ["year", "month"],
        "cols": "Product category",
    }
    """
    TOTAL = "Total"
    VALUES = "Values"

    def __init__(
        self,
        config: Optional[dict] = None,
        source: Optional[DataFrame] = None,
    ):
        self._config = Config(**config)
        self._config_changed = True
        self._data = source
        self._pivot = None

    def set_source(self, source: DataFrame) -> None:
        self._data = source

    def show(self, css: str = None) -> Styler:
        """Вычисляет и отображает сводную таблицу.
        
        :return: html объект с отображением сводной таблицы
        """
        css = css or (
            "tbody tr:nth-last-child(1) {background-color: lightblue;} "
            "tbody tr:hover {background-color: lightgreen;}"
        )
        self._pivot = self._make_pivot()
        stl = self._pivot.style
        stl.set_table_styles(parse_styles(css))
        return stl
    
    def _agg_dict(self) -> Dict[str, List[str]]:
        """Собирает словарь со всеми аггрегируемыми колонками и функциями."""
        agg = {}
        for val in self._config.vals:
            for col, agg_func in val.get_cols_to_aggregate().items():
                agg[col] = agg.get(col, set()) | {agg_func}
        return {k: list(v) for k, v in agg.items()}

    def _aggregate(
        self,
        dataframe: DataFrame,
        by: Optional[Union[str, List[str]]] = None,
    ) -> DataFrame:
        """"""
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

        for val in self._config.vals:
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
                names=values.index.names
            )
        else:
            totals.index.name = values.index.name

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
            values=[v.name for v in self._config.vals],
        )
        dataframe.index.name = None
        return dataframe

    def _make_pivot(self) -> DataFrame:
        rows = self._config.rows
        cols = self._config.cols
        
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
            values=[v.name for v in self._config.vals]
        )
        
        return self._concat(
            self._merge(values, row_totals),
            self._merge(col_totals, totals),
        )
    
    def _format(self, dataframe: DataFrame) -> DataFrame:
        for val in self._config.vals:
            if val.formatting:
                dataframe[""][[val.name]] = dataframe[""][[val.name]].apply(val.formatting)
                dataframe[self.TOTAL] = dataframe[self.TOTAL][[val.name]].apply(val.formatting)

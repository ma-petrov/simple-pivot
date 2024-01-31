import re
import numpy as np
import pandas as pd

from pandas import DataFrame
from typing import Any, Callable, Optional

from src.log import get_logger
from src.exceptions import (
    AggColError,
    IncorrectExpressionFormatError,
    ValueTypeError,
)


logger = get_logger(__name__)


class DataFormat:
    ...


def default_format_func(x: Any) -> str:
    return str(x)


def agg_computable_expression(
    data: DataFrame,
    expression: Callable,
    agg_func: Callable,
) -> Any:
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
    col_names = expression.__code__.co_varnames
    return expression(*[agg_func(data[c]) for c in col_names])

        
def agg(
    data: DataFrame,
    agg_col: str | Callable,
    agg_func: Optional[Callable] = None,
    format_func: Optional[DataFormat] = None,
) -> str:
    """Вычисляет результат аггрегации столбца или вычислимого выражения.
    
    :param data: DataFrame.
    :param agg_col: название столбца или функция.
    :param agg_func: функция аггрегирования, по умолчанию сумма.
    :param format_func: функция форматирования результата.
    
    :return: строка, содержащая отформатированное значение результата.
    """
    format_func = format_func or default_format_func
    agg_func = agg_func or sum

    if isinstance(agg_col, str) and agg_col in data.columns:
        result = agg_func(data[agg_col])

    elif isinstance(agg_col, Callable):
        result = agg_computable_expression(data, agg_col)

    else:
        raise AggColError()

    return format_func(result)

        
def make_pivot(
    data: DataFrame,
    rows,
    cols,
    agg_col,
    func=np.sum,
    data_format = None
) -> DataFrame:
    row_values = data[rows].unique() # значения столбца rows в исходном датафрейме (строки сводника)
    row_values.sort()
    index = [str(v) for v in row_values] + ["total"]
    pivot = {}
    last_col = agg_col
    # если задан разрез по столбцам, вычисление столбцов
    
    if cols != None:
        last_col = "total"
        col_values = data[cols].unique() # значения столбца cols в исходном датафрейме (колонки сводника)
        col_values = sorted(col_values)
        for col in col_values:
            agg_values = []
            for row in row_values:
                df_slice = data[(data[cols] == col) & (data[rows] == row)]
                agg_values.append(agg(df_slice, agg_col, func, data_format))
            df_slice = data[data[cols] == col]
            agg_values.append(agg(df_slice, agg_col, func, data_format))
            pivot.update({col: agg_values})
  
    # вычисление итогов по строкам
    agg_values = []
    for row in row_values:
        df_slice = data[data[rows] == row]
        agg_values.append(agg(df_slice, agg_col, func, data_format))
    agg_values.append(agg(data, agg_col, func, data_format))
    pivot.update({last_col: agg_values})
    # резузльтат
    return pd.DataFrame(pivot, index)


from re import findall
from typing import Any, Callable, Dict, List, Optional
from pandas import DataFrame, Series
from pandas.io.formats.style import Styler

def parse_styles(css: str) -> List[Dict[str, str]]:
    """Функция парсит обычный .css файл и заполняет список со словарями
    для передачи в качестве аргумента в функцию Style.set_table_styles().
    
    :param css: строка css файла
    
    :return: аргумент функции Style.set_table_styles()
    """
    selec_ptr = r'[\w\-][\w\-:\s\(\)]+[\w\-\)]'
    props_ptr = r'\{[\w\-:;\s]+\}'
    clear_props_ptr = r'\{[\s]*([\w\-:;\s]+[\w\-:;])[\s]*\}'
    styles = findall(f'{selec_ptr}[\s\n]+{props_ptr}', css)
    styles_list = list()
    for s in styles:
        selector = findall(selec_ptr, s)[0]
        props = findall(clear_props_ptr, s)[0]
        styles_list.append({'selector': selector, 'props': props})
    return styles_list

def show(dataframe: DataFrame, css: str = None) -> Styler:
    """Функция создает Style объект из DataFrame и применяет к нему стиль
    из переменной css, переменная css - строка с синтаксисом css файла.
    
    :param dataframe: исходный dataframe
    :param css: строка с синтаксисом css
    
    :return: отформатированный style объект
    """
    css = css or (
        "tbody tr:nth-last-child(1) {background-color: lightblue;} "
        "tbody tr:hover {background-color: lightgreen;}"
    )
    stl = dataframe.style
    stl.set_table_styles(parse_styles(css))
    return stl

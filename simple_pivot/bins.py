from typing import Any, Iterable
from pandas import DataFrame


def search_bin_index(
    l: Iterable,
    f: callable,
    target: Any,
) -> int:
    """Ищет индекс элемента итерируемого объекта такого, что значение функции f
    от l и элемента по этому индексу равно или приближено target.

    Если точного значения не найдено, то вернет индекс элемента, в котором
    значение функции будет наиболее приближенно к target снизу. Функция f
    должна содержать два аргумента, объект в котором выполняется поиск, индекс
    элемента.
    
    :param l: итерируемый объект, в котором выполняется поиск.
    :param f: функция таргета.
    :param t: значение таргета.
    
    :return: индекс элемента
    """
    left, right, middle = 0, len(l), len(l) // 2

    while left < right:
        if (v := f(l, middle)) == target:
            return middle

        if target > v:
            left = middle + 1
        else:
            right = middle - 1
        
        middle = (left + right) // 2
        
    return middle


def sum_of_slice(l: Iterable, i: int) -> Any:
    """Возвращает сумму элементов итерируемого объекта с 0 по i элемент."""
    return sum(l[:i + 1])


def make_bins_by_agg_col(
    data: DataFrame,
    binning_col: str,
    agg_col: str,
    nbins: int = None,
) -> list[Any]:
    """Вычисляет значения грниц бинов колонки binnig_col на освное равномерного
    распределения суммы в каждом бине колонки agg_col.
    
    :param data: датафрейм.
    :param binnig_col: название колонки, которую нужно разбить на бины.
    :param agg_col: название колонки, сумма значений которой дложна равномерно
    распределиться в каждом бине.
    :param nbins: кол-во бинов

    :return: возвращает список длиной nbins - 1 с граничным значениями бинов.
    """
    nbins = nbins or 2

    data.sort_values(by=binning_col, ascending=True).reset_index(inplace=True)
    c = data[agg_col]
    s = c.sum() / nbins
    bins = []

    for i in range(1, nbins):
        index = search_bin_index(c, sum_of_slice, s * i)
        bins.append(data.loc[index, binning_col])

    return bins

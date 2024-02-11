from re import findall
from typing import Dict, List


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

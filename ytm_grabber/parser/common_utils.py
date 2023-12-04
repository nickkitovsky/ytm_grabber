"""Common utils for parsing."""
import functools
from typing import Callable, Iterable
from unicodedata import normalize


def extract_chain(
    json_obj: dict | list,
    chain: Iterable | None = None,
) -> list | dict | str | None:
    """
    Extract chain keys from dict or list, skipping signle nested element (len==1). If last argument 'runs', it will be\
    automatically joined to str.

    Args:
        json_obj (dict | list): the object from witch the data will be extracted
        chain (Iterable | None, optional): chain of keys whitch will be extracted.\
            If chain is None, extract only single nested element. Defaults to None.

    Returns:
        list | dict | str | None: object after parsing
    """
    if chain:
        for element in chain:
            while len(json_obj) == 1:
                match json_obj:
                    case list(json_obj):
                        json_obj = json_obj[0]
                    case dict(json_obj) if element in json_obj:
                        break
                    case dict(json_obj):
                        json_obj = list(json_obj.values())[0]

            json_obj = json_obj[element]
        if chain[-1] == 'runs':
            json_obj = extract_runs(runs_list=json_obj)
    else:
        while len(json_obj) == 1:
            match json_obj:
                case list(json_obj):
                    json_obj = json_obj[0]
                case dict(json_obj):
                    json_obj = list(json_obj.values())[0]
    return json_obj


def normalize_unicode(func: Callable):
    """Use as decorator. Normalize unicode text.

    Args:
        func (Callable): the function should return str

    Returns:
        _type_: _description_
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        function_result = func(*args, **kwargs)
        if isinstance(function_result, str):
            return normalize('NFKD', function_result)
        raise TypeError('function should return str value')

    return wrapper


# TODO: Normalize to parametr, not decorator
@normalize_unicode
def extract_runs(runs_list: list, separator: str | None = '') -> str:
    """
    Join list's fields in 'runs' object to str.

    Args:
        runs_list (list): 'runs' elements contains list.
        separator (str, optional): separator in returnted string. Defaults to ' '.

    Returns:
        str: string which joined from 'runs' element.
    """
    return f'{separator}'.join([field['text'] for field in runs_list])

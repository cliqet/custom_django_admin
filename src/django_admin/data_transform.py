import re
import types
from typing import Any, Callable, List


def to_snake_case(camel_case_str: str) -> str:
    """ converts camel case string to snake case string """
    pattern = re.compile(r'(?<!^)(?=[A-Z])')
    try:
        camel_case_str = pattern.sub('_', camel_case_str).lower()
    except TypeError:
        ...
    return camel_case_str

def to_camel_case(snake_str: str) -> str:
    """ converts snake case string to camel case string """
    try:
        components = snake_str.split('_')
    except (ValueError, AttributeError):
        return snake_str
    return components[0] + ''.join(x.title() for x in components[1:])

def transform_dict_to_camel_case(data: dict, include_list = True) -> dict:
    """
        Convert keys of dict to camel case. Includes nested dicts and
        dicts in list. When include_list = False, dicts in list are not included
    """
    new_dict: dict = {}
    for key, value in data.items():
        if isinstance(value, dict):
            new_dict[to_camel_case(key)] = transform_dict_to_camel_case(
                data[key]
            )
        elif isinstance(value, list) and include_list:
            new_dict[to_camel_case(key)] = [
                transform_dict_to_camel_case(item)
                if isinstance(item, dict) or isinstance(item, list)
                else item
                for item in value        
            ]
        else:
            new_dict[to_camel_case(key)] = value
    return new_dict

def transform_dict_to_snake_case(data: dict, include_list = True) -> dict:
    """
        Convert keys of dict to snake case. Includes nested dicts and
        dicts in list. When include_list = False, dicts in list are not included
    """
    new_dict: dict = {}
    for key, value in data.items():
        if isinstance(value, dict):
            new_dict[to_snake_case(key)] = transform_dict_to_snake_case(
                data[key]
            )
        elif isinstance(value, list) and include_list:
            new_dict[to_snake_case(key)] = [
                transform_dict_to_snake_case(item)
                if isinstance(item, dict) or isinstance(item, list)
                else item
                for item in value
            ]
        else:
            new_dict[to_snake_case(key)] = value
    return new_dict

def destructure_list(arr: list,
                    extract: List[str],
                    apply_funcs: List[Callable[..., Any] | None] | None = None) -> List[Any]:
    """
        @param arr: The list used as source to unpack values
        @param extract: The list of items to unpack from the source. Use the ...rest keyword
            at the end to get remaining items that were not unpacked from the source arr. Use _
            to ignore item from the returned list
        @param apply_funcs: Optional list of functions or None to apply for each item extracted.
            Requires to be of the same length as the list extract. Use None if no function
            is to be applied to the item. Returned value after applying function is the one
            included in the returned list of this function
        @return a new list of unpacked items (transformed if any functions are applied)
        E.g. my_arr = [1, 2, 3, 4, 5]
            a, b, c = destructure_list(my_arr, ['a', 'b', 'c']) -> a = 1, b = 2, c = 3

            a, b, c = destructure_list(my_arr, ['a', 'b', '...rest']) -> a = 1, b = 2, c = [3, 4, 5]

            a, b = destructure_list(my_arr, ['a', '_', '...rest']) -> a = 1, b = [3, 4, 5]

            a, b, c = destructure_list(my_arr, ['a', 'b', '...rest'], [double, double, sum])
            -> a = 2, b = 4, c = 12 where double is a user-defined function and sum is a built-in function
    """
    # checks if arr is of type list
    if not isinstance(arr, list):
        raise TypeError(f'{arr} is not of type list')
    # checks if there are enough arguments to unpack from arr
    if len(extract) > len(arr):
        raise ValueError(f'{arr} does not have enough items to unpack')
    # checks if apply_funcs argument is present
    if apply_funcs:
        if len(extract) != len(apply_funcs):
            raise SyntaxError('Number of arguments in extract should match number of funcs')
    else:
        apply_funcs = [None for i in range(len(extract))]

    # find first instance of keyword rest and raise error when it is not the last argument in extract list
    try:
        index = extract.index('...rest')

        # check that rest keyword should be the last item in extract list if it is present
        if index != len(extract) - 1:
            raise SyntaxError('rest keyword should be the last item in extract list')
    except ValueError:
        # rest keyword is not mandatory in extract list
        pass

    # the new list to return
    new_arr = []

    # create a copy of arr
    arr_copy = [*arr]

    for arg, func in zip(extract, apply_funcs):
        # make sure each item in extract is of type string
        if not isinstance(arg, str):
            raise SyntaxError('extract list should only contain strings')
        # make sure func is a valid function if there is one
        if func and not(isinstance(func, types.FunctionType) or isinstance(func, types.BuiltinFunctionType)):
            raise SyntaxError(f'{func} is not a valid function')
        if arg != '...rest':
            # check if item is not needed
            if arg == '_':
                arr_copy.pop(0)
                continue
            # apply function if any
            if func:
                popped_item = func(arr_copy.pop(0))
            else:
                popped_item = arr_copy.pop(0)
            new_arr.append(popped_item)
        else:
            if func:
                remaining_items = func(arr_copy)
            else:
                remaining_items = arr_copy
            new_arr.append(remaining_items)
    return new_arr


def destructure_dict(obj: dict,
                    keys: List[str],
                    apply_funcs: List[Callable[..., Any] | None] | None = None) -> List[Any]:
    """
        @param obj: The dict used as source to unpack items
        @param keys: The list of keys searched for in obj. To access nested keys,
            use -> to separate each key. If key is not found, None is returned
        @param apply_funcs: Optional list of functions or None to apply for each item extracted.
            Requires to be of the same length as the list keys. Use None if no function
            is to be applied to the item. Returned value after applying function is the one
            included in the returned list of this function
        @return a new list of unpacked items (transformed if any functions are applied). If key
            is not found, even in nested keys where obj[key1][key2][key3] and key2 does not exist,
            item returned will be None
        E.g.
            def double(num):
                return num * 2
            my_obj = {
                'name': 'mike',
                'age': 23,
                'family_members': ['aiyi', 'mikel', 'micah'],
                'work': {
                    'company': 'Company A',
                    'years': 1
                }
            }
            a, b = destructure_dict(my_obj, ['age', 'work->company'], apply_funcs=[double, len])
            // a = 46, b = 8
    """
    # checks if obj is of type dict
    if not isinstance(obj, dict):
        raise TypeError(f'{obj} is not of type dict')
    # checks if functions argument is present
    if apply_funcs:
        if len(keys) != len(apply_funcs):
            raise SyntaxError('Number of arguments in keys should match number of funcs')
    else:
        apply_funcs = [None for i in range(len(keys))]

    # the new list to return
    object_list = []

    for key, func in zip(keys, apply_funcs):
        # make sure each item in keys is of type string
        if not isinstance(key, str):
            raise SyntaxError('keys list should only contain strings')
        # make sure func is a valid function if there is one
        if func and not(isinstance(func, types.FunctionType) or isinstance(func, types.BuiltinFunctionType)):
            raise SyntaxError(f'{func} is not a valid function')

        # if key passed is nested
        if '->' in key:
            multi_keys = key.split('->')
            item = obj
            for k in multi_keys:
                item = item.get(k)
                if not item:
                    item = None
                    break
        else:
            item = obj.get(key)

        if item:
            # apply function if any
            if func:
                item = func(item)
        object_list.append(item)
    return object_list
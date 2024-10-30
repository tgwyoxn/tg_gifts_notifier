import numpy as np


def pretty_int(number: int) -> str:
    return "{:,}".format(number)


def pretty_float(number: float, get_is_same: bool=False) -> tuple[str, bool] | str:
    formatted_number = float("{:.1g}".format(float(number)))
    formatted_number_str: str = np.format_float_positional(formatted_number, trim='-')

    if get_is_same:
        return (
            formatted_number_str,
            formatted_number == number
        )

    return formatted_number_str

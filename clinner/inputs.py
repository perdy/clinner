import typing

from clinner.console import console, error_console

T = typing.TypeVar("T")

__all__ = ["bool", "choices", "default"]


def bool(input_str: str) -> bool:
    """
    Prints a message asking for a yes/no response, otherwise it will continue asking.

    :param input_str: Message to print.
    :return: User response.
    """
    input_str = input_str + " [Y|n] "
    result = None
    while result is None:
        response = console.input(input_str)
        if response in ("", "y", "Y"):
            result = True
        elif response in ("n", "N"):
            result = False
        else:
            error_console.print(":cross_mark:  Wrong option")

    return result


def choices(input_str: str, choices: typing.List[T]) -> T:
    """
    Prints a message asking for a choice of given values.

    :param input_str: Message to print.
    :param choices: Choices.
    :return: User response.
    """
    choices = dict(enumerate(choices))
    input_str = "\n".join([input_str] + ["{:>3d}: {}".format(i, c) for i, c in choices.items()] + ["Choice: "])
    result = None
    while result is None:
        try:
            response = int(console.input(input_str))

            if response in choices.keys():
                result = choices[response]
            else:
                raise ValueError
        except ValueError:
            error_console.print(":cross_mark:  Wrong option")

    return result


def default(input_str: str, default: typing.Any) -> str:
    """
    Prints a message offering a default value.

    :param input_str: Message to print.
    :param default: Default value.
    :return: User response.
    """
    return console.input(f"{input_str} [{default!s}]: ") or default

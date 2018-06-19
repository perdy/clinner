from typing import Any, List


def bool_input(input_str: str) -> str:
    """
    Prints a message asking for a yes/no response, otherwise it will continue asking.

    :param input_str: Message to print.
    :return: User response.
    """
    input_str = input_str + " [Y|n] "
    result = None
    while result is None:
        response = input(input_str)
        if response in ("", "y", "Y"):
            result = True
        elif response in ("n", "N"):
            result = False
        else:
            print("Wrong option")

    return result


def choices_input(input_str: str, choices: List[Any]) -> str:
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
            response = int(input(input_str))

            if response in choices.keys():
                result = choices[response]
            else:
                raise ValueError
        except ValueError:
            print("Wrong option")

    return result


def default_input(input_str: str, default: Any = None) -> str:
    """
    Prints a message offering a default value.

    :param input_str: Message to print.
    :param default: Default value.
    :return: User response.
    """

    if default is None:
        default = ""

    input_str = input_str + " [{}]: ".format(default)
    return input(input_str) or default

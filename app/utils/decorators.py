from typing import Callable, Union

USER_IDENTIFIERS = ("id", "username", "mention")
CHAT_IDENTIFIERS = ("id", "username", "invite link")
DURATION = "duration"


def doc_args(*args: Union[str, tuple]) -> callable:
    """
    Provide arguments for a command handler,
    they will appear in auto-generated Telecharm guide.

    This decorator supports multiple args,
    each one is treated as a different argument in the guide.
    """

    def decorate_handler(func: Callable) -> Callable:
        new_values = []
        for value in args:
            if isinstance(value, str):
                value = (value,)
            elif not isinstance(value, tuple):
                raise TypeError("Every value must be either a tuple or str.")

            new_values.append(value)

        if not hasattr(func, "documented_args"):
            func.documented_args = []

        func.documented_args += new_values  # noqa
        return func

    return decorate_handler


def doc_exclude(obj=None) -> callable:
    """Exclude a handler from the Telecharm auto-generated guide."""

    def decorate_handler(func: Callable) -> Callable:
        func.no_documentation = True
        return func

    if obj is None:
        return decorate_handler
    else:
        return decorate_handler(obj)

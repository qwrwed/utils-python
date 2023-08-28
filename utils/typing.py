from typing import Callable, TypeVar

C = TypeVar("C", bound=Callable)  # parameterize over all callables


def copy_signature(template: C) -> Callable[[C], C]:
    """
    Decorator to copy the static signature between functions
    https://stackoverflow.com/a/65288734
    """

    def apply_signature(target: C) -> C:
        # copy runtime inspectable metadata as well
        try:
            target.__annotations__ = template.__annotations__
        except AttributeError:
            pass
        return target

    return apply_signature

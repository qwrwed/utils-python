import operator
from argparse import ArgumentParser, Namespace
from functools import reduce
from types import UnionType
from typing import Any, Self


def remove_none_type(tp: type[Any]) -> type[Any]:
    if isinstance(tp, UnionType):
        args = tuple(t for t in tp.__args__ if t is not type(None))
        if not args:
            return type(None)
        elif len(args) == 1:
            return args[0]
        else:
            return reduce(operator.or_, args)
    elif tp in (None, type(None)):
        raise TypeError("Cannot remove None type from None type")
    else:
        return tp


class BaseNamespace(Namespace):
    @classmethod
    def parse_args(cls, parser: ArgumentParser | None = None) -> Self:
        if parser is None:
            parser = ArgumentParser()
        namespace = cls()
        for attr_name, attr_type in cls.__annotations__.items():
            if hasattr(cls, attr_name):
                default = getattr(cls, attr_name)
                required = False
            else:
                default = None
                required = True

            type_without_none = remove_none_type(attr_type)
            if isinstance(type_without_none, UnionType):
                raise TypeError(f"UnionType ({type_without_none!r}) not supported for args")

            namespace.__dict__[attr_name] = default
            if attr_type is bool:
                parser.add_argument(
                    f"--{attr_name.replace('_', '-')}",
                    action=f"store_{str(not default).lower()}",
                )
            else:
                parser.add_argument(
                    f"--{attr_name.replace('_', '-')}",
                    type=type_without_none,
                    default=default,
                    required=required,
                    help="Default: %(default)r",
                )
        args = parser.parse_args(namespace=namespace)
        return args

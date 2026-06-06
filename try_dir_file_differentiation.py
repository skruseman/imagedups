""" Demonstrates type generics ! """

from abc import ABC, abstractmethod
from typing import Generic, Iterable, TypeVar, cast

T = TypeVar('T')


the_items = ['a', 10, 11, 'b', 12]


class ItemHandler(ABC, Generic[T]):

    @abstractmethod
    def print(self, item: T):
        pass

class StrHandler(ItemHandler[str]):

    def print(self, item: str):
        print(f'String {item}')

class IntHandler(ItemHandler[int]):

    def print(self, item: int):
        print(f'Int {item}')


def _get_handler(item) -> StrHandler | IntHandler:
    if isinstance(item, str):
        return StrHandler()
    if isinstance(item, int):
        return IntHandler()
    raise TypeError(f"Unsupported item type: {type(item).__name__}")


def do_items(items: Iterable[int | str]):
    """ Allows mixed input."""
    _do_items(items)

def do_strs(strs: Iterable[str]):
    _do_items(strs, StrHandler())

def do_ints(ints: Iterable[int]):
    _do_items(ints, IntHandler())

def _do_items(items: Iterable[str | int], handler: StrHandler | IntHandler | None = None):
    """In this design static typing won't help me prevent cases where a type
    specific handler is passed while the input contains items of a different type."""
    with open('some_file', 'w') as f:
        for item in items:
            handler_ = handler or _get_handler(item)
            handler_ = cast(ItemHandler[str | int], handler_)

            handler_.print(item)
            f.write(f'{item}\n')


do_items(the_items)
print()
do_strs([item for item in the_items if isinstance(item, str)])
print()
do_ints([item for item in the_items if isinstance(item, int)])

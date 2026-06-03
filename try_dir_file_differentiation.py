from abc import ABC, abstractmethod
from typing import List, Optional


the_items = ['a', 10, 11, 'b', 12]


class ItemHandler(ABC):

    @abstractmethod
    def print(self, item: str|int):
        pass

class StrHandler(ItemHandler):

    def print(self, item: str):
        print(f'String {item}')

class IntHandler(ItemHandler):

    def print(self, item: int):
        print(f'Int {item}')


def _get_handler(item) -> ItemHandler:
    if isinstance(item, str):
        return StrHandler()
    else:
        return IntHandler()


def do_items(items: List[int|str]):
    _do_items(items)

def do_strs(strs: List[str]):
    _do_items(strs, StrHandler())

def do_ints(ints: List[int]):
    _do_items(ints, IntHandler())

def _do_items(items: List[int|str], handler: Optional[StrHandler|IntHandler] = None):
    for item in items:
        handler_ = handler if handler else _get_handler(item)
        handler_.print(item)


do_items(the_items)
print()
do_strs([item for item in the_items if isinstance(item, str)])
print()
do_ints([item for item in the_items if isinstance(item, int)])

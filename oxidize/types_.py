from typing import TypeVar


T = TypeVar("T")
E = TypeVar("E")


class Err[T, E]:
    err: E

    @property
    def is_ok(self) -> bool:
        return False

    @property
    def is_err(self) -> bool:
        return not self.is_ok

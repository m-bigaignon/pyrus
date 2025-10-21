"""Implementation of the Option and Result types.

Inspired by the Rust standard library. The API is not an exact match to the Rust API,
for various reasons. Some methods don't make sense in Python, some have simply not been
deemed necessary at the time of writing.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import (
    TypeVar,
    cast,
    override,
)


T = TypeVar("T")
E = TypeVar("E")


class UnwrapError(Exception):
    """Incorrect unwrapping of a container."""


class OptionProtocol[T](ABC):
    """Defines the Option API."""

    @abstractmethod
    def and_then[U](self, f: Callable[[T], "Option[U]"]) -> "Option[U]":
        """Returns Nothing if the option is Nothing, otherwise calls f."""

    @abstractmethod
    def expect(self, msg: str) -> T:
        """Return the contained value.

        Raises an exception with the given message if the option is None.
        """

    @abstractmethod
    def filter(self, predicate: Callable[[T], bool]) -> "Option[T]":
        """Return None if the option is Nothing. Otherwise transforms the result.

        Transformation occurs by applying the predicate to the contained value.
        If the predicate returns True, returns Option[T]. Otherwise returns Nothing.
        """

    @abstractmethod
    def flatten(self) -> "Option[T]":
        """Removes one level of nested Option."""

    @property
    @abstractmethod
    def is_nothing(self) -> bool:
        """Returns whether this Option is Nothing."""

    @property
    @abstractmethod
    def is_some(self) -> bool:
        """Returns whether this Option is Some."""

    @abstractmethod
    def map[U](self, f: Callable[[T], U]) -> "Option[U]":
        """Maps an Option[T] to Option[U] by applying a function to the inner value.

        Returns Nothing if the option is nothing.
        """

    @abstractmethod
    def map_or[U](self, default: U, f: Callable[[T], U]) -> U:
        """Returns the provided default result (if nothing) or map the option."""

    @abstractmethod
    def map_or_else[U](self, default: Callable[[], U], f: Callable[[T], U]) -> U:
        """Computes a default function result (if nothing) or map the option."""

    @abstractmethod
    def ok_or[E](self, err: E) -> "Result[T, E]":
        """Transforms the Option into a result.

        This maps Some(v) to Ok(v) and None to Err(err).
        """

    @abstractmethod
    def ok_or_else[E](self, f: Callable[[], E]) -> "Result[T, E]":
        """Transforms the Option into a result.

        This maps Some(v) to Ok(v) and None to Err(err()).
        """

    def unwrap(self) -> T:
        """Returns the contained value or raises an exception."""
        return self.expect("called `Option.unwrap()` on a `Nothing` value")

    @abstractmethod
    def unwrap_or(self, default: T) -> T:
        """Returns the contained value or the default value."""

    @abstractmethod
    def unwrap_or_else(self, f: Callable[[], T]) -> T:
        """Returns the contained value or calls the function."""

    @abstractmethod
    def or_else(self, f: Callable[[], "Option[T]"]) -> "Option[T]":
        """Returns the option if it's some, or calls f."""

    @abstractmethod
    def zip(self, other: "Option[T]") -> "Option[tuple[T, T]]":
        """Zips self with another non-empty option."""

    @abstractmethod
    def __contains__(self, item: T) -> bool:
        """Returns True if the Option contains the given value."""


@dataclass(eq=True, frozen=True)
class Some(OptionProtocol[T]):
    """An Option containing a value."""

    value: T

    @override
    def and_then[U](self, f: Callable[[T], "Option[U]"]) -> "Option[U]":
        return f(self.value)

    @override
    def expect(self, msg: str) -> T:
        return self.value

    @override
    def filter(self, predicate: Callable[[T], bool]) -> "Option[T]":
        return self if predicate(self.value) else Nothing()

    @override
    def flatten(self) -> "Option[T]":
        t = self.unwrap()
        if isinstance(t, OptionProtocol):
            return cast("Option", t)
        return self

    @property
    @override
    def is_nothing(self) -> bool:
        return False

    @property
    @override
    def is_some(self) -> bool:
        return True

    @override
    def map[U](self, f: Callable[[T], U]) -> "Option[U]":
        return Some(f(self.value))

    @override
    def map_or[U](self, default: U, f: Callable[[T], U]) -> U:
        return f(self.value)

    @override
    def map_or_else[U](self, default: Callable[[], U], f: Callable[[T], U]) -> U:
        return f(self.value)

    @override
    def ok_or[E](self, err: E) -> "Result[T, E]": ...

    @override
    def ok_or_else[E](self, f: Callable[[], E]) -> "Result[T, E]": ...

    @override
    def unwrap_or(self, default: T) -> T:
        return self.value

    @override
    def unwrap_or_else(self, f: Callable[[], T]) -> T:
        return self.value

    @override
    def or_else(self, f: Callable[[], "Option[T]"]) -> "Option[T]":
        return self

    @override
    def zip(self, other: "Option[T]") -> "Option[tuple[T, T]]":
        return Some((self.unwrap(), other.unwrap())) if other.is_some else Nothing()

    @override
    def __contains__(self, item: T) -> bool:
        return item == self.value


@dataclass(eq=True, frozen=True)
class Nothing(OptionProtocol[T]):
    """An Option containing nothing."""

    @override
    def and_then[U](self, f: Callable[[T], "Option[U]"]) -> "Option[U]":
        return Nothing()

    @override
    def expect(self, msg: str) -> T:
        raise UnwrapError(msg)

    @override
    def filter(self, predicate: Callable[[T], bool]) -> "Option[T]":
        return self

    @override
    def flatten(self) -> "Option[T]":
        return self

    @property
    @override
    def is_nothing(self) -> bool:
        return True

    @property
    @override
    def is_some(self) -> bool:
        return False

    @override
    def map[U](self, f: Callable[[T], U]) -> "Option[U]":
        return Nothing()

    @override
    def map_or[U](self, default: U, f: Callable[[T], U]) -> U:
        return default

    @override
    def map_or_else[U](self, default: Callable[[], U], f: Callable[[T], U]) -> U:
        return default()

    @override
    def ok_or[E](self, err: E) -> "Result[T, E]": ...

    @override
    def ok_or_else[E](self, f: Callable[[], E]) -> "Result[T, E]": ...

    @override
    def unwrap_or(self, default: T) -> T:
        return default

    @override
    def unwrap_or_else(self, f: Callable[[], T]) -> T:
        return f()

    @override
    def or_else(self, f: Callable[[], "Option[T]"]) -> "Option[T]":
        return f()

    @override
    def zip(self, other: "Option[T]") -> "Option[tuple[T, T]]":
        return Nothing()

    @override
    def __contains__(self, item: T) -> bool:
        return False


Option = Nothing[T] | Some[T]


class ResultProtocol[T, E](ABC):
    """Defines the Result API."""

    @property
    @abstractmethod
    def is_err(self) -> bool:
        """Returns whether this Result is an Err."""

    @property
    @abstractmethod
    def is_ok(self) -> bool:
        """Returns whether this Result is an Ok."""


class Ok(ResultProtocol[T, E]):
    """A Result containing a value."""

    @property
    @override
    def is_err(self) -> bool:
        return False

    @property
    @override
    def is_ok(self) -> bool:
        return True


class Err(ResultProtocol[T, E]):
    """A Result containing an error."""

    @property
    @override
    def is_err(self) -> bool:
        return True

    @property
    @override
    def is_ok(self) -> bool:
        return False


Result = Ok[T, E] | Err[T, E]

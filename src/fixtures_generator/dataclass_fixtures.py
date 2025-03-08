import enum
import typing
import dataclasses
from .factory_fixtures import (
    int_factory,
    float_factory,
    str_factory,
)

__all__ = (
    'SimpleDataclass',
    'SimpleDefaultsDataclass',
    'SimpleDefaultFactoriesDataclass',
    'OptionalDataclass',
    'XID',
    'YID',
    'ZS',
    'OneTwo',
    'FirstSecond',
    'SubtypesDataclass',
)


@dataclasses.dataclass
class SimpleDataclass:
    x: int
    y: float
    z: str


@dataclasses.dataclass
class SimpleDefaultsDataclass:
    x: int = 1
    y: float = 1.1
    z: str = 'hello'


@dataclasses.dataclass
class SimpleDefaultFactoriesDataclass:
    x: int = dataclasses.field(default_factory=int_factory)
    y: float = dataclasses.field(default_factory=float_factory)
    z: str = dataclasses.field(default_factory=str_factory)


@dataclasses.dataclass
class OptionalDataclass:
    x: int
    y: typing.Optional[float]
    z: typing.List[typing.Optional[str]]
    d: typing.Dict[str, int]
    s: SimpleDataclass


# region sub_classes
class XID(int):
    pass


YID = typing.NewType('YID', float)


class ZS(str):
    pass


class OneTwo(enum.Enum):
    ONE = 'one'
    TWO = 'two'


class FirstSecond(enum.IntEnum):
    FIRST = 1
    SECOND = 2


@dataclasses.dataclass
class SubtypesDataclass:
    x: XID
    y: YID
    z: ZS
    one_two: OneTwo
    first_second: FirstSecond
    simple: SimpleDataclass
# endregion subclasses

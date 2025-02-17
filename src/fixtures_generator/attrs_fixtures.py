import typing
import attr
from .factory_fixtures import (
    int_factory,
    float_factory,
    str_factory,
)

__all__ = (
    'SimpleAttrs',
    'SimpleDefaultsAttrs',
    'SimpleDefaultFactoriesAttrs',
    'OptionalAttrs',
)


@attr.s
class SimpleAttrs:
    xx: int = attr.ib()
    yy: float = attr.ib()
    zz: str = attr.ib()


@attr.s
class SimpleDefaultsAttrs:
    xx: int = attr.ib(default=1)
    yy: float = attr.ib(default=1.1)
    zz: str = attr.ib(default='hello')


@attr.s
class SimpleDefaultFactoriesAttrs:
    xx: int = attr.ib(factory=int_factory)
    yy: float = attr.ib(factory=float_factory)
    zz: str = attr.ib(factory=str_factory)


@attr.s
class OptionalAttrs:
    x: int = attr.ib()
    y: typing.Optional[float] = attr.ib()
    z: typing.List[typing.Optional[str]] = attr.ib()
    d: typing.Dict[str, int] = attr.ib()
    s: SimpleAttrs = attr.ib()

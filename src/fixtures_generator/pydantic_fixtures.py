import typing
import pydantic
from .factory_fixtures import (
    int_factory,
    float_factory,
    str_factory,
)

# noinspection SpellCheckingInspection
__all__ = (
    'SimplePydantic',
    'SimpleDefaultsPydantic',
    'SimpleDefaultFactoriesPydantic',
    'OptionalPydantic',
)


# noinspection SpellCheckingInspection
class SimplePydantic(pydantic.BaseModel):
    xxx: int
    yyy: float
    zzz: str


# noinspection SpellCheckingInspection
class SimpleDefaultsPydantic(pydantic.BaseModel):
    xxx: int = 1
    yyy: float = 1.1
    zzz: str = 'hello'


# noinspection SpellCheckingInspection
class SimpleDefaultFactoriesPydantic(pydantic.BaseModel):
    xxx: int = pydantic.Field(default_factory=int_factory)
    yyy: float = pydantic.Field(default_factory=float_factory)
    zzz: str = pydantic.Field(default_factory=str_factory)


# noinspection SpellCheckingInspection
class OptionalPydantic(pydantic.BaseModel):
    xxx: int
    yyy: typing.Optional[float]
    zzz: typing.List[typing.Optional[str]]
    ddd: typing.Dict[str, int]
    sss: SimplePydantic

import typing
import pytest
from unittest.mock import patch, Mock
import fixtures_generator.pydantic_fixtures_generator as tm
from fixtures_generator.factory_fixtures import (
    int_factory,
    float_factory,
    str_factory,
)
from fixtures_generator.pydantic_fixtures import (
    SimplePydantic,
    SimpleDefaultsPydantic,
    SimpleDefaultFactoriesPydantic,
    OptionalPydantic,
)


# noinspection SpellCheckingInspection
class NotPydantic:
    pass


# noinspection SpellCheckingInspection
class TestPydanticFixtureGenerator:
    def test_inheritance(self):
        assert issubclass(tm.PydanticFixturesGenerator, tm.DataclassFixturesGenerator)

    def test__validate(self):
        tm.PydanticFixturesGenerator._validate(SimplePydantic)
        tm.PydanticFixturesGenerator._validate(SimpleDefaultsPydantic)
        tm.PydanticFixturesGenerator._validate(SimpleDefaultFactoriesPydantic)

        with pytest.raises(tm.IsNotPydanticError):
            tm.PydanticFixturesGenerator._validate(typing.cast(typing.Type[SimplePydantic], 'foo'))

        with pytest.raises(tm.IsNotPydanticError):
            tm.PydanticFixturesGenerator._validate(typing.cast(typing.Type[SimplePydantic], NotPydantic))

    def test__get_fields(self):
        assert tm.PydanticFixturesGenerator._get_fields(SimplePydantic) == (
            tm.FieldInfo(field_name='xxx', field_type=int, default_value=None, default_factory=None),
            tm.FieldInfo(field_name='yyy', field_type=float, default_value=None, default_factory=None),
            tm.FieldInfo(field_name='zzz', field_type=str, default_value=None, default_factory=None),
        )
        assert tm.PydanticFixturesGenerator._get_fields(SimpleDefaultsPydantic) == (
            tm.FieldInfo(field_name='xxx', field_type=int, default_value=1, default_factory=None),
            tm.FieldInfo(field_name='yyy', field_type=float, default_value=1.1, default_factory=None),
            tm.FieldInfo(field_name='zzz', field_type=str, default_value='hello', default_factory=None),
        )
        assert tm.PydanticFixturesGenerator._get_fields(SimpleDefaultFactoriesPydantic) == (
            tm.FieldInfo(field_name='xxx', field_type=int, default_value=None, default_factory=int_factory),
            tm.FieldInfo(field_name='yyy', field_type=float, default_value=None, default_factory=float_factory),
            tm.FieldInfo(field_name='zzz', field_type=str, default_value=None, default_factory=str_factory),
        )

    def test__is_dataclass(self):
        assert tm.PydanticFixturesGenerator._is_dataclass(
            tm.FieldInfo(field_name='fff', field_type=SimplePydantic, default_value=None, default_factory=None)
        ) is True
        assert tm.PydanticFixturesGenerator._is_dataclass(
            tm.FieldInfo(field_name='fff', field_type=tm.FieldInfo, default_value=None, default_factory=None)
        ) is False  # means we are not going to mix pydantic models and @dataclasses.dataclass
        assert tm.PydanticFixturesGenerator._is_dataclass(
            tm.FieldInfo(field_name='fff', field_type=int, default_value=None, default_factory=None)
        ) is False
        assert tm.PydanticFixturesGenerator._is_dataclass(
            tm.FieldInfo(field_name='fff', field_type=typing.List[int], default_value=None, default_factory=None)
        ) is False
        assert tm.PydanticFixturesGenerator._is_dataclass(
            tm.FieldInfo(field_name='fff', field_type=typing.Optional[int], default_value=None, default_factory=None)
        ) is False

    @patch.object(
        tm.DataclassFixturesGenerator, tm.DataclassFixturesGenerator._generate_int.__name__, Mock(return_value=33)
    )
    @patch.object(
        tm.DataclassFixturesGenerator, tm.DataclassFixturesGenerator._generate_float.__name__, Mock(return_value=.3)
    )
    @patch.object(
        tm.DataclassFixturesGenerator, tm.DataclassFixturesGenerator._generate_str.__name__, Mock(return_value='x')
    )
    def test_generate_fixtures(self):
        result = tm.PydanticFixturesGenerator.generate_fixtures(cls_=SimplePydantic)
        assert result == [SimplePydantic(xxx=33, yyy=0.3, zzz='x')]

        result = tm.PydanticFixturesGenerator.generate_fixtures(cls_=OptionalPydantic)
        assert result == [
            OptionalPydantic(xxx=33, yyy=0.3, zzz=['x'], ddd={'x': 33}, sss=SimplePydantic(xxx=33, yyy=0.3, zzz='x')),
            OptionalPydantic(xxx=33, yyy=0.3, zzz=[None], ddd={'x': 33}, sss=SimplePydantic(xxx=33, yyy=0.3, zzz='x')),
            OptionalPydantic(xxx=33, yyy=None, zzz=['x'], ddd={'x': 33}, sss=SimplePydantic(xxx=33, yyy=0.3, zzz='x')),
            OptionalPydantic(xxx=33, yyy=None, zzz=[None], ddd={'x': 33}, sss=SimplePydantic(xxx=33, yyy=0.3, zzz='x')),
        ]

    def test_generate_fixtures__defaults(self):
        result = tm.PydanticFixturesGenerator.generate_fixtures(cls_=SimpleDefaultsPydantic)
        assert result == [SimpleDefaultsPydantic()]

        result = tm.PydanticFixturesGenerator.generate_fixtures(cls_=SimpleDefaultFactoriesPydantic)
        assert result == [SimpleDefaultFactoriesPydantic()]

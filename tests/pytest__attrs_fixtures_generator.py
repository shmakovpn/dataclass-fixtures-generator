import typing
import pytest
from unittest.mock import patch, Mock
import fixtures_generator.attrs_fixtures_generator as tm
from fixtures_generator.factory_fixtures import (
    int_factory,
    float_factory,
    str_factory,
)
from fixtures_generator.attrs_fixtures import (
    SimpleAttrs,
    SimpleDefaultsAttrs,
    SimpleDefaultFactoriesAttrs,
    OptionalAttrs,
)


class NotAttrs:
    pass


class TestAttrsFixturesGenerator:
    def test_inheritance(self):
        assert issubclass(tm.AttrsFixturesGenerator, tm.DataclassFixturesGenerator)

    def test_validate(self):
        tm.AttrsFixturesGenerator._validate(SimpleAttrs)
        tm.AttrsFixturesGenerator._validate(SimpleDefaultsAttrs)
        tm.AttrsFixturesGenerator._validate(SimpleDefaultFactoriesAttrs)

        with pytest.raises(tm.IsNotAttrsError):
            tm.AttrsFixturesGenerator._validate(typing.cast(typing.Type[SimpleAttrs], 'bar'))

        with pytest.raises(tm.IsNotAttrsError):
            tm.AttrsFixturesGenerator._validate(NotAttrs)

    def test__get_fields(self):
        assert tm.AttrsFixturesGenerator._get_fields(SimpleAttrs) == (
            tm.FieldInfo(field_name='xx', field_type=int, default_value=None, default_factory=None),
            tm.FieldInfo(field_name='yy', field_type=float, default_value=None, default_factory=None),
            tm.FieldInfo(field_name='zz', field_type=str, default_value=None, default_factory=None),
        )
        assert tm.AttrsFixturesGenerator._get_fields(SimpleDefaultsAttrs) == (
            tm.FieldInfo(field_name='xx', field_type=int, default_value=1, default_factory=None),
            tm.FieldInfo(field_name='yy', field_type=float, default_value=1.1, default_factory=None),
            tm.FieldInfo(field_name='zz', field_type=str, default_value='hello', default_factory=None),
        )
        assert tm.AttrsFixturesGenerator._get_fields(SimpleDefaultFactoriesAttrs) == (
            tm.FieldInfo(field_name='xx', field_type=int, default_value=None, default_factory=int_factory),
            tm.FieldInfo(field_name='yy', field_type=float, default_value=None, default_factory=float_factory),
            tm.FieldInfo(field_name='zz', field_type=str, default_value=None, default_factory=str_factory),
        )

    def test__is_dataclass(self):
        assert tm.AttrsFixturesGenerator._is_dataclass(
            tm.FieldInfo(field_name='ff', field_type=SimpleAttrs, default_value=None, default_factory=None)
        ) is True
        assert tm.AttrsFixturesGenerator._is_dataclass(
            tm.FieldInfo(field_name='ff', field_type=tm.FieldInfo, default_value=None, default_factory=None)
        ) is False  # means we are not going to mix @attr.s and @dataclasses.dataclass
        assert tm.AttrsFixturesGenerator._is_dataclass(
            tm.FieldInfo(field_name='ff', field_type=int, default_value=None, default_factory=None)
        ) is False
        assert tm.AttrsFixturesGenerator._is_dataclass(
            tm.FieldInfo(field_name='ff', field_type=typing.List[int], default_value=None, default_factory=None)
        ) is False
        assert tm.AttrsFixturesGenerator._is_dataclass(
            tm.FieldInfo(field_name='ff', field_type=typing.Optional[int], default_value=None, default_factory=None)
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
        result = tm.AttrsFixturesGenerator.generate_fixtures(cls_=SimpleAttrs)
        assert result == [SimpleAttrs(xx=33, yy=0.3, zz='x')]

        result = tm.AttrsFixturesGenerator.generate_fixtures(cls_=OptionalAttrs)
        assert result == [
            OptionalAttrs(x=33, y=0.3, z=['x'], d={'x': 33}, s=SimpleAttrs(xx=33, yy=0.3, zz='x')),
            OptionalAttrs(x=33, y=0.3, z=[None], d={'x': 33}, s=SimpleAttrs(xx=33, yy=0.3, zz='x')),
            OptionalAttrs(x=33, y=None, z=['x'], d={'x': 33}, s=SimpleAttrs(xx=33, yy=0.3, zz='x')),
            OptionalAttrs(x=33, y=None, z=[None], d={'x': 33}, s=SimpleAttrs(xx=33, yy=0.3, zz='x')),
        ]

    def test_generate_fixtures__defaults(self):
        result = tm.AttrsFixturesGenerator.generate_fixtures(cls_=SimpleDefaultsAttrs)
        assert result == [SimpleDefaultsAttrs()]

        result = tm.AttrsFixturesGenerator.generate_fixtures(cls_=SimpleDefaultFactoriesAttrs)
        assert result == [SimpleDefaultFactoriesAttrs()]

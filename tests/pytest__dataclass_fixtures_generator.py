import typing
import pytest
import dataclasses
import fixtures_generator.dataclass_fixtures_generator as tm
from fixtures_generator.factory_fixtures import (
    int_factory,
    float_factory,
    str_factory,
)
from fixtures_generator.dataclass_fixtures import (
    SimpleDataclass,
    SimpleDefaultsDataclass,
    SimpleDefaultFactoriesDataclass,
    OptionalDataclass,
    XID,
    YID,
    ZS,
    OneTwo,
    SubtypesDataclass, FirstSecond,
)
from unittest.mock import patch, Mock
from one_patch import Op


class TestFieldInfo:
    def test_inheritance(self):
        assert len(tm.FieldInfo.mro()) == 2

    def test_is_dataclass(self):
        assert dataclasses.is_dataclass(tm.FieldInfo)


class NotDataclass:
    pass


class TestDataclassFixturesGenerator:
    def test__validate(self):
        tm.DataclassFixturesGenerator._validate(SimpleDataclass)
        tm.DataclassFixturesGenerator._validate(SimpleDefaultsDataclass)

        with pytest.raises(tm.IsNotDataclassError):
            tm.DataclassFixturesGenerator._validate(typing.cast(typing.Type[SimpleDataclass], 'foo'))

        with pytest.raises(tm.IsNotDataclassError):
            tm.DataclassFixturesGenerator._validate(NotDataclass)

    def test__get_fields(self):
        assert tm.DataclassFixturesGenerator._get_fields(SimpleDataclass) == (
            tm.FieldInfo(field_name='x', field_type=int, default_value=None, default_factory=None),
            tm.FieldInfo(field_name='y', field_type=float, default_value=None, default_factory=None),
            tm.FieldInfo(field_name='z', field_type=str, default_value=None, default_factory=None),
        )
        assert tm.DataclassFixturesGenerator._get_fields(SimpleDefaultsDataclass) == (
            tm.FieldInfo(field_name='x', field_type=int, default_value=1, default_factory=None),
            tm.FieldInfo(field_name='y', field_type=float, default_value=1.1, default_factory=None),
            tm.FieldInfo(field_name='z', field_type=str, default_value='hello', default_factory=None),
        )
        assert tm.DataclassFixturesGenerator._get_fields(SimpleDefaultFactoriesDataclass) == (
            tm.FieldInfo(field_name='x', field_type=int, default_value=None, default_factory=int_factory),
            tm.FieldInfo(field_name='y', field_type=float, default_value=None, default_factory=float_factory),
            tm.FieldInfo(field_name='z', field_type=str, default_value=None, default_factory=str_factory),
        )

    def test__is_dataclass(self):
        assert tm.DataclassFixturesGenerator._is_dataclass(
            tm.FieldInfo(field_name='f', field_type=tm.FieldInfo, default_value=None, default_factory=None)
        ) is True
        assert tm.DataclassFixturesGenerator._is_dataclass(
            tm.FieldInfo(field_name='f', field_type=int, default_value=None, default_factory=None)
        ) is False
        assert tm.DataclassFixturesGenerator._is_dataclass(
            tm.FieldInfo(field_name='f', field_type=typing.List[int], default_value=None, default_factory=None)
        ) is False
        assert tm.DataclassFixturesGenerator._is_dataclass(
            tm.FieldInfo(field_name='f', field_type=typing.Optional[int], default_value=None, default_factory=None)
        ) is False

    def test__validate_filed_type(self):
        field_info = tm.FieldInfo(
            field_name='f',
            field_type=typing.cast(type, None),
            default_value=None,
            default_factory=None,
        )
        with pytest.raises(tm.FieldTypeIsNoneError):
            tm.DataclassFixturesGenerator._validate_field_type(field_info=field_info)

        field_info = dataclasses.replace(field_info, field_type=int)
        tm.DataclassFixturesGenerator._validate_field_type(field_info=field_info)

    def test__is_union(self):
        assert tm.DataclassFixturesGenerator._is_union(
            tm.FieldInfo(field_name='fn', field_type=int, default_value=None, default_factory=None)
        ) is False
        assert tm.DataclassFixturesGenerator._is_union(
            tm.FieldInfo(field_name='fn', field_type=float, default_value=None, default_factory=None)
        ) is False
        assert tm.DataclassFixturesGenerator._is_union(
            tm.FieldInfo(field_name='fn', field_type=str, default_value=None, default_factory=None)
        ) is False
        assert tm.DataclassFixturesGenerator._is_union(
            tm.FieldInfo(field_name='fn', field_type=typing.Optional[int], default_value=None, default_factory=None)
        ) is True
        assert tm.DataclassFixturesGenerator._is_union(
            tm.FieldInfo(field_name='fn', field_type=typing.Optional[float], default_value=None, default_factory=None)
        ) is True
        assert tm.DataclassFixturesGenerator._is_union(
            tm.FieldInfo(field_name='fn', field_type=typing.Optional[str], default_value=None, default_factory=None)
        ) is True
        assert tm.DataclassFixturesGenerator._is_union(
            tm.FieldInfo(field_name='fn', field_type=typing.Union[int, float], default_value=None, default_factory=None)
        ) is True
        assert tm.DataclassFixturesGenerator._is_union(
            tm.FieldInfo(field_name='fn', field_type=typing.List[int], default_value=None, default_factory=None)
        ) is False
        assert tm.DataclassFixturesGenerator._is_union(
            tm.FieldInfo(field_name='fn', field_type=typing.Tuple[int], default_value=None, default_factory=None)
        ) is False
        assert tm.DataclassFixturesGenerator._is_union(
            tm.FieldInfo(field_name='fn', field_type=typing.Tuple[int, ...], default_value=None, default_factory=None)
        ) is False
        assert tm.DataclassFixturesGenerator._is_union(
            tm.FieldInfo(
                field_name='fn1',
                field_type=typing.Tuple[int, float],
                default_value=None,
                default_factory=None
            ),
        ) is False
        assert tm.DataclassFixturesGenerator._is_union(
            tm.FieldInfo(field_name='fn', field_type=typing.Set[int], default_value=None, default_factory=None)
        ) is False
        assert tm.DataclassFixturesGenerator._is_union(
            tm.FieldInfo(field_name='fn', field_type=typing.Dict[str, int], default_value=None, default_factory=None)
        ) is False
        assert tm.DataclassFixturesGenerator._is_union(
            tm.FieldInfo(field_name='fn', field_type=typing.FrozenSet[int], default_value=None, default_factory=None)
        ) is False
        assert tm.DataclassFixturesGenerator._is_union(
            tm.FieldInfo(
                field_name='fn',
                field_type=typing.List[typing.Union[str, int]],
                default_value=None,
                default_factory=None,
            )
        ) is False

    def test__is_collection(self):
        assert tm.DataclassFixturesGenerator._is_collection(
            tm.FieldInfo(field_name='f', field_type=int, default_value=None, default_factory=None)
        ) is False
        assert tm.DataclassFixturesGenerator._is_collection(
            tm.FieldInfo(field_name='f', field_type=typing.List[int], default_value=None, default_factory=None)
        ) is True
        assert tm.DataclassFixturesGenerator._is_collection(
            tm.FieldInfo(field_name='f', field_type=typing.Tuple[int], default_value=None, default_factory=None)
        ) is True
        assert tm.DataclassFixturesGenerator._is_collection(
            tm.FieldInfo(field_name='f', field_type=typing.Set[int], default_value=None, default_factory=None)
        ) is True
        assert tm.DataclassFixturesGenerator._is_collection(
            tm.FieldInfo(field_name='f', field_type=typing.FrozenSet[int], default_value=None, default_factory=None)
        ) is True
        assert tm.DataclassFixturesGenerator._is_collection(
            tm.FieldInfo(field_name='f', field_type=typing.Dict[str, int], default_value=None, default_factory=None)
        ) is False
        assert tm.DataclassFixturesGenerator._is_collection(
            tm.FieldInfo(field_name='f', field_type=typing.Union[str, int], default_value=None, default_factory=None)
        ) is False
        assert tm.DataclassFixturesGenerator._is_collection(
            tm.FieldInfo(
                field_name='f',
                field_type=typing.List[typing.Optional[int]],
                default_value=None,
                default_factory=None,
            )
        ) is True

    def test__is_dict(self):
        assert tm.DataclassFixturesGenerator._is_dict(
            tm.FieldInfo(field_name='f', field_type=typing.Dict[str, int], default_value=None, default_factory=None)
        ) is True
        assert tm.DataclassFixturesGenerator._is_dict(
            tm.FieldInfo(field_name='f', field_type=typing.Union[str, int], default_value=None, default_factory=None)
        ) is False
        assert tm.DataclassFixturesGenerator._is_dict(
            tm.FieldInfo(field_name='f', field_type=typing.List[int], default_value=None, default_factory=None)
        ) is False
        assert tm.DataclassFixturesGenerator._is_dict(
            tm.FieldInfo(field_name='f', field_type=typing.Tuple[int, ...], default_value=None, default_factory=None)
        ) is False
        assert tm.DataclassFixturesGenerator._is_dict(
            tm.FieldInfo(field_name='f', field_type=typing.Set[int], default_value=None, default_factory=None)
        ) is False
        assert tm.DataclassFixturesGenerator._is_dict(
            tm.FieldInfo(field_name='f', field_type=typing.FrozenSet[int], default_value=None, default_factory=None)
        ) is False

    def test__generate_int(self):
        assert tm.DataclassFixturesGenerator._generate_int(
            tm.FieldInfo(field_name='f', field_type=int, default_value=3, default_factory=None)
        ) == 3

        assert tm.DataclassFixturesGenerator._generate_int(
            tm.FieldInfo(field_name='r', field_type=int, default_value=None, default_factory=int_factory)
        ) == int_factory()

        assert isinstance(
            tm.DataclassFixturesGenerator._generate_int(
                tm.FieldInfo(field_name='r', field_type=int, default_value=None, default_factory=None)
            ),
            int,
        )

        values = [
            tm.DataclassFixturesGenerator._generate_int(
                tm.FieldInfo(field_name='r', field_type=int, default_value=None, default_factory=None)
            ) for _x in range(2)
        ]
        assert values[0] != values[1]

        with pytest.raises(tm.DefaultIntError):
            _r = tm.DataclassFixturesGenerator._generate_int(
                tm.FieldInfo(field_name='ni', field_type=int, default_value='foo', default_factory=None)
            )

        with pytest.raises(tm.DefaultIntFactoryError):
            _r = tm.DataclassFixturesGenerator._generate_int(
                tm.FieldInfo(field_name='ni', field_type=int, default_value=None, default_factory=str_factory)
            )

    def test__generate_float(self):
        assert tm.DataclassFixturesGenerator._generate_float(
            tm.FieldInfo(field_name='f', field_type=float, default_value=3.3, default_factory=None)
        ) == 3.3

        assert tm.DataclassFixturesGenerator._generate_float(
            tm.FieldInfo(field_name='r', field_type=float, default_value=None, default_factory=float_factory)
        ) == float_factory()

        assert isinstance(
            tm.DataclassFixturesGenerator._generate_float(
                tm.FieldInfo(field_name='r', field_type=float, default_value=None, default_factory=None)
            ),
            float,
        )

        values = [
            tm.DataclassFixturesGenerator._generate_float(
                tm.FieldInfo(field_name='r', field_type=float, default_value=None, default_factory=None)
            ) for _x in range(2)
        ]
        assert values[0] != values[1]

        with pytest.raises(tm.DefaultFloatError):
            _r = tm.DataclassFixturesGenerator._generate_float(
                tm.FieldInfo(field_name='nf', field_type=float, default_value='foo', default_factory=None)
            )

        with pytest.raises(tm.DefaultFloatFactoryError):
            _r = tm.DataclassFixturesGenerator._generate_float(
                tm.FieldInfo(field_name='nf', field_type=float, default_value=None, default_factory=str_factory)
            )

        with pytest.raises(tm.DefaultFloatError):
            _r = tm.DataclassFixturesGenerator._generate_float(
                tm.FieldInfo(field_name='nf', field_type=float, default_value=1, default_factory=None)
            )  # be strict, use 1.0 for float values, don't use 1

        with pytest.raises(tm.DefaultFloatFactoryError):
            _r = tm.DataclassFixturesGenerator._generate_float(
                tm.FieldInfo(field_name='nf', field_type=float, default_value=None, default_factory=int_factory)
            )  # be strict, use 1.0 for float values, don't use 1

    def test__generate_str(self):
        assert tm.DataclassFixturesGenerator._generate_str(
            tm.FieldInfo(field_name='f', field_type=str, default_value='oo', default_factory=None)
        ) == 'oo'

        assert tm.DataclassFixturesGenerator._generate_str(
            tm.FieldInfo(field_name='f', field_type=str, default_value=None, default_factory=str_factory)
        ) == str_factory()

        assert isinstance(
            tm.DataclassFixturesGenerator._generate_str(
                tm.FieldInfo(field_name='r', field_type=str, default_value=None, default_factory=None),
            ),
            str
        )

        values = [
            tm.DataclassFixturesGenerator._generate_str(
                tm.FieldInfo(field_name='r', field_type=str, default_value=None, default_factory=None),
            ) for _x in range(2)
        ]
        assert values[0] != values[1]

        with pytest.raises(tm.DefaultStrError):
            _r = tm.DataclassFixturesGenerator._generate_str(
                tm.FieldInfo(field_name='ns', field_type=str, default_value=1, default_factory=None)
            )

        with pytest.raises(tm.DefaultStrFactoryError):
            _r = tm.DataclassFixturesGenerator._generate_str(
                tm.FieldInfo(field_name='ns', field_type=str, default_value=None, default_factory=float_factory)
            )

    def test__generate_bool(self):
        assert tm.DataclassFixturesGenerator._generate_bool_s(
            tm.FieldInfo(field_name='b', field_type=bool, default_value=False, default_factory=None)
        ) == [False, True]

        assert tm.DataclassFixturesGenerator._generate_bool_s(
            tm.FieldInfo(field_name='b', field_type=bool, default_value=True, default_factory=None)
        ) == [True, False]

        assert tm.DataclassFixturesGenerator._generate_bool_s(
            tm.FieldInfo(field_name='b', field_type=bool, default_value=None, default_factory=lambda: False)
        ) == [False, True]

        assert tm.DataclassFixturesGenerator._generate_bool_s(
            tm.FieldInfo(field_name='b', field_type=bool, default_value=None, default_factory=lambda: True)
        ) == [True, False]

        assert tm.DataclassFixturesGenerator._generate_bool_s(
            tm.FieldInfo(field_name='b', field_type=bool, default_value=None, default_factory=None)
        ) == [True, False]

        with pytest.raises(tm.DefaultBoolError):
            _r = tm.DataclassFixturesGenerator._generate_bool_s(
                tm.FieldInfo(field_name='b', field_type=bool, default_value=0, default_factory=None)
            )

        with pytest.raises(tm.DefaultBoolError):
            _r = tm.DataclassFixturesGenerator._generate_bool_s(
                tm.FieldInfo(field_name='b', field_type=bool, default_value=1.0, default_factory=None)
            )

        with pytest.raises(tm.DefaultBoolFactoryError):
            _r = tm.DataclassFixturesGenerator._generate_bool_s(
                tm.FieldInfo(field_name='b', field_type=bool, default_value=None, default_factory=lambda: 0)
            )

        with pytest.raises(tm.DefaultBoolFactoryError):
            _r = tm.DataclassFixturesGenerator._generate_bool_s(
                tm.FieldInfo(field_name='b', field_type=bool, default_value=None, default_factory=lambda: None)
            )

    def test__generate_scalar_values(self):
        with Op(tm.DataclassFixturesGenerator._generate_scalar_values) as op:
            op.args.field_info.field_type = bool
            assert op.c(*op.args) == op.args.cls._generate_bool_s.return_value

            op.args.field_info.field_type = int
            assert op.c(*op.args) == [op.args.cls._generate_int.return_value]

            op.args.field_info.field_type = float
            assert op.c(*op.args) == [op.args.cls._generate_float.return_value]

            op.args.field_info.field_type = str
            assert op.c(*op.args) == [op.args.cls._generate_str.return_value]

            op.args.field_info.field_type = ...
            op.args.field_info.default_value = ...
            assert op.c(*op.args) == [...]

            op.args.field_info.default_value = None
            op.args.field_info.default_factory = lambda: 'foo'
            assert op.c(*op.args) == ['foo']

            op.args.field_info.default_factory = None
            assert op.c(*op.args) == [None]

    @patch.object(
        tm.DataclassFixturesGenerator, tm.DataclassFixturesGenerator._generate_int.__name__, Mock(return_value=33)
    )
    @patch.object(
        tm.DataclassFixturesGenerator, tm.DataclassFixturesGenerator._generate_float.__name__, Mock(return_value=.3)
    )
    @patch.object(
        tm.DataclassFixturesGenerator, tm.DataclassFixturesGenerator._generate_str.__name__, Mock(return_value='x')
    )
    def test__generate_union_values(self):
        field_info = tm.FieldInfo(
            field_name='fn', field_type=typing.Optional[int], default_value=None, default_factory=None
        )
        values = tm.DataclassFixturesGenerator._generate_union_values(field_info=field_info)
        assert values == [33, None]

        field_info = tm.FieldInfo(
            field_name='fn', field_type=typing.Optional[float], default_value=None, default_factory=None
        )
        values = tm.DataclassFixturesGenerator._generate_union_values(field_info=field_info)
        assert values == [0.3, None]

        field_info = tm.FieldInfo(
            field_name='fn', field_type=typing.Optional[str], default_value=None, default_factory=None
        )
        values = tm.DataclassFixturesGenerator._generate_union_values(field_info=field_info)
        assert values == ['x', None]

        field_info = tm.FieldInfo(
            field_name='fn', field_type=typing.Optional[bool], default_value=None, default_factory=None
        )
        values = tm.DataclassFixturesGenerator._generate_union_values(field_info=field_info)
        assert values == [True, False, None]

        field_info = tm.FieldInfo(
            field_name='fn',
            field_type=typing.Union[None, str, int, float, bool],
            default_value=None,
            default_factory=None,
        )
        values = tm.DataclassFixturesGenerator._generate_union_values(field_info=field_info)
        assert values == ['x', 0.3, 33, True, False, None]

        field_info = tm.FieldInfo(
            field_name='fn', field_type=typing.Optional[typing.List[int]], default_value=None, default_factory=None
        )
        values = tm.DataclassFixturesGenerator._generate_union_values(field_info=field_info)
        assert values == [[33], None]

    @patch.object(
        tm.DataclassFixturesGenerator, tm.DataclassFixturesGenerator._generate_int.__name__, Mock(return_value=33)
    )
    @patch.object(
        tm.DataclassFixturesGenerator, tm.DataclassFixturesGenerator._generate_float.__name__, Mock(return_value=.3)
    )
    @patch.object(
        tm.DataclassFixturesGenerator, tm.DataclassFixturesGenerator._generate_str.__name__, Mock(return_value='x')
    )
    def test__generate_collection_values(self):
        field_info = tm.FieldInfo(
            field_name='fn',
            field_type=typing.List[int],
            default_value=None,
            default_factory=None,
        )
        assert tm.DataclassFixturesGenerator._generate_collection_values(field_info=field_info) == [[33]]

        field_info = dataclasses.replace(field_info, field_type=typing.Set[float])
        assert tm.DataclassFixturesGenerator._generate_collection_values(field_info=field_info) == [{0.3}]

        field_info = dataclasses.replace(field_info, field_type=typing.FrozenSet[str])
        assert tm.DataclassFixturesGenerator._generate_collection_values(field_info=field_info) == [{'x'}]

        field_info = dataclasses.replace(field_info, field_type=typing.Tuple[int, float, None])
        result = tm.DataclassFixturesGenerator._generate_collection_values(field_info=field_info)
        assert result == [(0.3,), (33,), (None,)]

        field_info = dataclasses.replace(field_info, field_type=typing.List[typing.Optional[int]])
        assert tm.DataclassFixturesGenerator._generate_collection_values(field_info=field_info) == [[33], [None]]

        field_info = dataclasses.replace(field_info, field_type=typing.Set[typing.Optional[float]])
        assert tm.DataclassFixturesGenerator._generate_collection_values(field_info=field_info) == [{0.3}, {None}]

        field_info = dataclasses.replace(field_info, field_type=typing.FrozenSet[typing.Optional[str]])
        assert tm.DataclassFixturesGenerator._generate_collection_values(field_info=field_info) == [{'x'}, {None}]

        field_info = dataclasses.replace(
            field_info,
            field_type=typing.Tuple[typing.Optional[int], typing.Optional[float], typing.Optional[str]],
        )
        result = tm.DataclassFixturesGenerator._generate_collection_values(field_info=field_info)
        assert result == [('x',), (0.3,), (33,), (None,)]

    def test__generate_collection_values__defaults(self):
        field_info = tm.FieldInfo(
            field_name='fn',
            field_type=typing.List[int],
            default_value=[22],
            default_factory=None,
        )
        assert tm.DataclassFixturesGenerator._generate_collection_values(field_info=field_info) == [[22]]

        field_info = dataclasses.replace(field_info, field_type=typing.Set[float], default_value={0.3})
        assert tm.DataclassFixturesGenerator._generate_collection_values(field_info=field_info) == [{0.3}]

        field_info = dataclasses.replace(field_info, field_type=typing.FrozenSet[str], default_value={'x'})
        assert tm.DataclassFixturesGenerator._generate_collection_values(field_info=field_info) == [{'x'}]

        field_info = dataclasses.replace(field_info, field_type=typing.Tuple[int, float, None], default_value=(22,))
        assert tm.DataclassFixturesGenerator._generate_collection_values(field_info=field_info) == [(22,)]

    @patch.object(
        tm.DataclassFixturesGenerator, tm.DataclassFixturesGenerator._generate_int.__name__, Mock(return_value=33)
    )
    @patch.object(
        tm.DataclassFixturesGenerator, tm.DataclassFixturesGenerator._generate_float.__name__, Mock(return_value=.3)
    )
    @patch.object(
        tm.DataclassFixturesGenerator, tm.DataclassFixturesGenerator._generate_str.__name__, Mock(return_value='x')
    )
    def test__generate_dict_values(self):
        field_info = tm.FieldInfo(
            field_name='fn',
            field_type=typing.Dict[int, int],
            default_value=None,
            default_factory=None,
        )
        result = tm.DataclassFixturesGenerator._generate_dict_values(field_info=field_info)
        assert result == [{33: 33}]

        field_info = dataclasses.replace(field_info, field_type=typing.Dict[str, float])
        result = tm.DataclassFixturesGenerator._generate_dict_values(field_info=field_info)
        assert result == [{'x': 0.3}]

    def test__generate_dict_values__defaults(self):
        field_info = tm.FieldInfo(
            field_name='fn',
            field_type=typing.Dict[str, int],
            default_value={'xx': 22},
            default_factory=None,
        )
        assert tm.DataclassFixturesGenerator._generate_dict_values(field_info=field_info) == [{'xx': 22}]

        field_info = dataclasses.replace(field_info, default_value=None, default_factory=lambda: {'z': 2})
        assert tm.DataclassFixturesGenerator._generate_dict_values(field_info=field_info) == [{'z': 2}]

    @patch.object(
        tm.DataclassFixturesGenerator, tm.DataclassFixturesGenerator._generate_int.__name__, Mock(return_value=33)
    )
    @patch.object(
        tm.DataclassFixturesGenerator, tm.DataclassFixturesGenerator._generate_float.__name__, Mock(return_value=.3)
    )
    @patch.object(
        tm.DataclassFixturesGenerator, tm.DataclassFixturesGenerator._generate_str.__name__, Mock(return_value='x')
    )
    def test__generate_dataclass_values(self):
        result = tm.DataclassFixturesGenerator._generate_dataclass_values(field_info=tm.FieldInfo(
            field_name='fn',
            field_type=SimpleDataclass,
            default_value=None,
            default_factory=None,
        ))
        assert result == [SimpleDataclass(x=33, y=0.3, z='x')]

    def test__generate_dataclass_values__defaults(self):
        simple_dataclass = SimpleDataclass(x=1, y=1.1, z='_z')
        field_info = tm.FieldInfo(
            field_name='fn',
            field_type=SimpleDataclass,
            default_value=simple_dataclass,
            default_factory=None,
        )
        assert tm.DataclassFixturesGenerator._generate_dataclass_values(field_info=field_info) == [simple_dataclass]

        field_info = dataclasses.replace(field_info, default_value=None, default_factory=lambda: simple_dataclass)
        assert tm.DataclassFixturesGenerator._generate_dataclass_values(field_info=field_info) == [simple_dataclass]

    @patch.object(
        tm.DataclassFixturesGenerator, tm.DataclassFixturesGenerator._generate_int.__name__, Mock(return_value=33)
    )
    @patch.object(
        tm.DataclassFixturesGenerator, tm.DataclassFixturesGenerator._generate_float.__name__, Mock(return_value=.3)
    )
    @patch.object(
        tm.DataclassFixturesGenerator, tm.DataclassFixturesGenerator._generate_str.__name__, Mock(return_value='x')
    )
    @patch.object(
        tm.DataclassFixturesGenerator,
        tm.DataclassFixturesGenerator._generate_enum.__name__,
        side_effect=lambda field_info: (
            FirstSecond.FIRST if issubclass(field_info.field_type, int) else OneTwo.TWO
        ),
    )
    def test_generate_fixtures(self, m_enum):
        result = tm.DataclassFixturesGenerator.generate_fixtures(cls_=SimpleDataclass)
        assert result == [SimpleDataclass(x=33, y=0.3, z='x')]

        result = tm.DataclassFixturesGenerator.generate_fixtures(cls_=OptionalDataclass)
        assert result == [
            OptionalDataclass(x=33, y=0.3, z=['x'], d={'x': 33}, s=SimpleDataclass(x=33, y=0.3, z='x')),
            OptionalDataclass(x=33, y=0.3, z=[None], d={'x': 33}, s=SimpleDataclass(x=33, y=0.3, z='x')),
            OptionalDataclass(x=33, y=None, z=['x'], d={'x': 33}, s=SimpleDataclass(x=33, y=0.3, z='x')),
            OptionalDataclass(x=33, y=None, z=[None], d={'x': 33}, s=SimpleDataclass(x=33, y=0.3, z='x')),
        ]

        result = tm.DataclassFixturesGenerator.generate_fixtures(cls_=SubtypesDataclass)
        assert result == [
            SubtypesDataclass(
                x=XID(33),
                y=YID(0.3),
                z=ZS('x'),
                one_two=OneTwo.TWO,
                first_second=FirstSecond.FIRST,
                simple=SimpleDataclass(x=33, y=0.3, z='x'),
            ),
        ]

    def test_new_type(self):
        result = tm.DataclassFixturesGenerator.generate_fixtures(cls_=SubtypesDataclass)
        assert isinstance(result[0].x, XID)
        assert isinstance(result[0].z, ZS)
        assert result[0].one_two in [OneTwo.ONE, OneTwo.TWO]

    def test_generate_fixtures__defaults(self):
        result = tm.DataclassFixturesGenerator.generate_fixtures(cls_=SimpleDefaultsDataclass)
        assert result == [SimpleDefaultsDataclass()]

        result = tm.DataclassFixturesGenerator.generate_fixtures(cls_=SimpleDefaultFactoriesDataclass)
        assert result == [SimpleDefaultFactoriesDataclass()]


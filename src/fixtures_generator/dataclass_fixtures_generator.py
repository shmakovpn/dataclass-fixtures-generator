import typing
import sys
import enum
import abc
import dataclasses
import random
import string
import itertools
import inspect

__all__ = (
    'FieldTypeIsNoneError',
    'DefaultIntError',
    'DefaultIntFactoryError',
    'DefaultFloatError',
    'DefaultFloatFactoryError',
    'DefaultStrError',
    'DefaultStrFactoryError',
    'DefaultEnumError',
    'DefaultEnumFactoryError',
    'DefaultBoolError',
    'DefaultBoolFactoryError',
    'FieldInfo',
    'DataclassFixturesGenerator',
)


class IsNotDataclassError(TypeError):
    """
    Provided argument is not a dataclass
    """
    pass


class FieldTypeIsNoneError(ValueError):
    """provided field type is None"""
    pass


class DefaultIntError(ValueError):
    """Provided default value for int type is not integer"""
    pass


class DefaultIntFactoryError(ValueError):
    """Provided default factory returned not integer value for int type"""
    pass


class DefaultFloatError(ValueError):
    """Provided default value for float type is not float"""
    pass


class DefaultFloatFactoryError(ValueError):
    """Provided default factory returned not float value for float type"""
    pass


class DefaultStrError(ValueError):
    """Provided default value for str type is not string"""
    pass


class DefaultStrFactoryError(ValueError):
    """Provided default factory returned not string value for str type"""
    pass


class DefaultEnumError(ValueError):
    """Provided default value for enum type is not enum"""


class DefaultEnumFactoryError(ValueError):
    """Provided default factory returned not enum value for enum type"""


class DefaultBoolError(ValueError):
    """Provided default value for bool type is not boolean"""
    pass


class DefaultBoolFactoryError(ValueError):
    """Provided default factory returned not boolean value for bool type"""
    pass


_T = typing.TypeVar('_T')


@dataclasses.dataclass(frozen=True)
class FieldInfo:
    field_name: str
    field_type: typing.Type[typing.Any]
    default_value: typing.Optional[typing.Any]
    default_factory: typing.Optional[typing.Any]


class DataclassFixturesGenerator(abc.ABC):
    _types_order: typing.Dict[typing.Type, int] = {type(None): 0, bool: 100, int: 200, float: 300, str: 400}

    @classmethod
    def _validate(cls, cls_: typing.Type) -> None:
        """validate that cls_ is dataclass"""
        if not dataclasses.is_dataclass(cls_):
            raise IsNotDataclassError(f'{cls_} is not a dataclass')

    @classmethod
    def _validate_field_type(cls, field_info: FieldInfo) -> None:
        if field_info.field_type is None:
            raise FieldTypeIsNoneError(f'field name=={field_info.field_name} has None type')

    @classmethod
    def _get_fields(cls, cls_: typing.Type) -> typing.Tuple[FieldInfo, ...]:
        fields: typing.Tuple[dataclasses.Field, ...] = dataclasses.fields(cls_)

        field: dataclasses.Field
        fields_info: typing.Tuple[FieldInfo, ...] = tuple(
            FieldInfo(
                field_name=field.name,
                field_type=typing.cast(typing.Type[typing.Any], field.type),
                default_value=field.default if field.default != dataclasses.MISSING else None,
                default_factory=field.default_factory if field.default_factory != dataclasses.MISSING else None,
            ) for field in fields
        )
        return fields_info

    @classmethod
    def _is_union(cls, field_info: FieldInfo) -> bool:
        """True if field has Union type"""
        if typing.get_origin(field_info.field_type) is typing.Union:
            return True

        return False

    @classmethod
    def _is_collection(cls, field_info: FieldInfo) -> bool:
        """True if field has list, tuple, set or frozenset type"""
        if typing.get_origin(field_info.field_type) in {list, tuple, set, frozenset}:
            return True

        return False

    @classmethod
    def _is_dict(cls, field_info: FieldInfo) -> bool:
        """True if field has Dict type"""
        if typing.get_origin(field_info.field_type) is dict:
            return True

        return False

    @classmethod
    def _is_dataclass(cls, field_info: FieldInfo) -> bool:
        """True if field is dataclass"""
        if dataclasses.is_dataclass(field_info.field_type):
            return True

        return False

    @classmethod
    def _generate_int(cls, field_info: FieldInfo) -> int:
        if field_info.default_value is not None:
            if isinstance(field_info.default_value, int):
                return field_info.default_value

            raise DefaultIntError(f'provided default value=={field_info.default_value} for int type is not integer')

        if field_info.default_factory:
            value = field_info.default_factory()
            if isinstance(value, int):
                return value

            raise DefaultIntFactoryError(f'Provided default factory returned not integer value=={value} for int type')

        return field_info.field_type(random.randint(0, 10000))

    @classmethod
    def _generate_float(cls, field_info: FieldInfo) -> float:
        if field_info.default_value is not None:
            if isinstance(field_info.default_value, float):
                return field_info.default_value

            raise DefaultFloatError(f'provided default value=={field_info.default_value} for float type is not float')

        if field_info.default_factory:
            value = field_info.default_factory()
            if isinstance(value, float):
                return value

            raise DefaultFloatFactoryError(f'Provided default factory returned not float value=={value} for float type')

        return field_info.field_type(random.uniform(0.0, 10000.0))

    @classmethod
    def _generate_str(cls, field_info: FieldInfo) -> str:
        if field_info.default_value is not None:
            if isinstance(field_info.default_value, str):
                return field_info.default_value

            raise DefaultStrError(f'provided default value=={field_info.default_value} for str type is not string')

        if field_info.default_factory:
            value = field_info.default_factory()
            if isinstance(value, str):
                return value

            raise DefaultStrFactoryError(f'Provided default factory returned not string value=={value} for str type')

        value_: str = ''.join(random.choices(string.ascii_letters, k=5))
        return field_info.field_type(value_)

    @classmethod
    def _generate_enum(cls, field_info: FieldInfo) -> enum.Enum:
        if field_info.default_value is not None:
            if isinstance(field_info.default_value, enum.Enum):
                return field_info.default_value

            raise DefaultEnumError(f'provided default value=={field_info.default_value} for enum type is not enum')

        if field_info.default_factory:
            value = field_info.default_factory()
            if isinstance(value, enum.Enum):
                return value

            raise DefaultEnumFactoryError(f'Provided default factory returned not enum value=={value} for enum type')

        return field_info.field_type(random.choice(list(typing.cast(typing.Iterable, field_info.field_type))))

    @classmethod
    def _generate_bool_s(cls, field_info: FieldInfo) -> typing.List[bool]:
        if isinstance(field_info.default_value, bool):
            return [field_info.default_value, not field_info.default_value]

        if field_info.default_value is not None:
            raise DefaultBoolError(f'provided default value=={field_info.default_value} for bool type is not boolean')

        if field_info.default_factory:
            value = field_info.default_factory()
            if isinstance(value, bool):
                return [value, not value]

            raise DefaultBoolFactoryError(f'Provided default factory returned not boolean value=={value} for bool type')

        return [True, False]

    @classmethod
    def _generate_scalar_values(cls, field_info: FieldInfo) -> typing.List[typing.Any]:
        if inspect.isclass(field_info.field_type) and field_info.field_type is not ...:
            if issubclass(field_info.field_type, bool):
                return cls._generate_bool_s(field_info=field_info)

            if issubclass(field_info.field_type, int) and not issubclass(field_info.field_type, enum.Enum):
                return [cls._generate_int(field_info=field_info)]

            if issubclass(field_info.field_type, float):
                return [cls._generate_float(field_info=field_info)]

            if issubclass(field_info.field_type, str):
                return [cls._generate_str(field_info=field_info)]

            if issubclass(field_info.field_type, enum.Enum):
                return [cls._generate_enum(field_info=field_info)]

        if field_info.default_value:
            return [field_info.default_value]

        if field_info.default_factory:
            return [field_info.default_factory()]

        return [None]

    @classmethod
    def _generate_union_values(cls, field_info: FieldInfo) -> typing.List[typing.Any]:
        types: typing.List[typing.Type] = sorted(
            set(typing.get_args(field_info.field_type)),
            key=lambda type_: cls._types_order.get(type_, 500),
            reverse=True,
        )

        return list(
            itertools.chain.from_iterable(
                cls._generate_values(
                    field_info=FieldInfo(
                        field_name=field_info.field_name,
                        field_type=type_,
                        default_value=field_info.default_value if type_ else None,
                        default_factory=field_info.default_factory if type_ else None,
                    )
                )
                for type_ in types
            ),
        )

    @classmethod
    def _generate_collection_values(cls, field_info: FieldInfo) -> typing.List[typing.Any]:
        if field_info.default_value is not None:
            return [field_info.default_value]
        elif field_info.default_factory:
            default_value: typing.Any = field_info.default_factory()
            return [default_value]

        origin: typing.Type = typing.cast(type, typing.get_origin(field_info.field_type))  # List|Tuple|Set|Frozenset
        types: typing.Tuple[typing.Type, ...] = typing.cast(
            typing.Tuple[typing.Type, ...],
            typing.get_args(field_info.field_type)
        )
        values: typing.List[typing.Any] = [
            v for v in itertools.chain.from_iterable([
                cls._generate_values(
                    field_info=FieldInfo(
                        field_name=field_info.field_name,
                        field_type=tp,
                        default_value=None,
                        default_factory=None,
                    )
                )
                for tp in types
            ])
        ]

        sorted_values: typing.List[typing.Any] = sorted(
            set(values),
            key=lambda v: cls._types_order.get(type(v), 500),
            reverse=True,
        )
        return [origin([v]) for v in sorted_values]

    @classmethod
    def _generate_dict_values(cls, field_info: FieldInfo) -> typing.List[typing.Any]:
        if field_info.default_value is not None:
            return [field_info.default_value]
        elif field_info.default_factory:
            default_value: typing.Any = field_info.default_factory()
            return [default_value]

        key_type: typing.Type[typing.Any]
        value_type: typing.Type[typing.Any]
        key_type, value_type = typing.get_args(field_info.field_type)
        key_values = cls._generate_values(field_info=FieldInfo(
            field_name=field_info.field_name,
            field_type=key_type,
            default_value=None,
            default_factory=None,
        ))
        value_values = cls._generate_values(field_info=FieldInfo(
            field_name=field_info.field_name,
            field_type=value_type,
            default_value=None,
            default_factory=None,
        ))
        return [{k: v} for k, v in zip(key_values, value_values)]

    @classmethod
    def _generate_dataclass_values(cls, field_info: FieldInfo) -> typing.List[typing.Any]:
        if field_info.default_value is not None:
            return [field_info.default_value]
        elif field_info.default_factory:
            default_value: typing.Any = field_info.default_factory()
            return [default_value]

        fields_values: typing.List[typing.List[typing.Any]] = []
        fields: typing.Tuple[FieldInfo, ...] = cls._get_fields(cls_=field_info.field_type)
        field_names: typing.List[str] = [f.field_name for f in fields]
        field: FieldInfo
        for field in fields:
            field_values: typing.List[typing.Any] = cls._generate_values(field_info=field)
            fields_values.append(field_values)

        return [
            field_info.field_type(**dict(zip(field_names, combination)))
            for combination in itertools.product(*fields_values)
        ]

    @classmethod
    def _generate_values(cls, field_info: FieldInfo) -> typing.List[typing.Any]:
        # region NewType
        if str(field_info.field_type).startswith('<function NewType.<locals>.new_type'):
           field_info = dataclasses.replace(field_info, field_type=getattr(field_info.field_type, '__supertype__'))

        if sys.version_info >= (3, 10):
            if isinstance(field_info.field_type, typing.cast(type, typing.NewType)):
                field_info = dataclasses.replace(field_info, field_type=getattr(field_info.field_type, '__supertype__'))
        # endregion NewType

        cls._validate_field_type(field_info=field_info)

        values: typing.List[typing.Any]
        if cls._is_union(field_info=field_info):
            values = cls._generate_union_values(field_info=field_info)
            return values

        if cls._is_collection(field_info=field_info):
            values = cls._generate_collection_values(field_info=field_info)
            return values

        if cls._is_dict(field_info=field_info):
            values = cls._generate_dict_values(field_info=field_info)
            return values

        if cls._is_dataclass(field_info=field_info):
            values = cls._generate_dataclass_values(field_info=field_info)
            return values

        values = cls._generate_scalar_values(field_info=field_info)

        return values

    @classmethod
    def generate_fixtures(cls, cls_: typing.Type[_T]) -> typing.List[_T]:
        """Generate fixtures for dataclass"""
        cls._validate(cls_=cls_)
        return cls._generate_dataclass_values(field_info=FieldInfo(
            field_name='-',
            field_type=cls_,
            default_value=None,
            default_factory=None,
        ))

import typing
import attr
from .dataclass_fixtures_generator import FieldInfo, DataclassFixturesGenerator

__all__ = (
    'IsNotAttrsError',
    'AttrsFixturesGenerator',
)


class IsNotAttrsError(TypeError):
    """
    Provided argument is not an attrs dataclass
    """
    pass


class AttrsFixturesGenerator(DataclassFixturesGenerator):
    @classmethod
    def _validate(cls, cls_: typing.Type) -> None:
        """validate that cls_ is attrs dataclass"""
        if not attr.has(cls_):
            raise IsNotAttrsError(f'{cls_} is not an attrs dataclass')

    @classmethod
    def _get_fields(cls, cls_: typing.Type) -> typing.Tuple[FieldInfo, ...]:
        fields: typing.Tuple[attr.Attribute, ...] = attr.fields(cls_)

        field: attr.Attribute
        fields_info: typing.Tuple[FieldInfo, ...] = tuple(
            FieldInfo(
                field_name=field.name,
                field_type=typing.cast(type, field.type),
                default_value=(
                    field.default if (
                        field.default != attr.NOTHING
                        and not isinstance(field.default, typing.cast(typing.Type, attr.Factory))
                    ) else None
                ),
                default_factory=(
                    getattr(field.default, 'factory') if (
                        field.default != attr.NOTHING
                        and isinstance(field.default, typing.cast(typing.Type, attr.Factory))
                    ) else None
                ),
            ) for field in fields
        )
        return fields_info

    @classmethod
    def _is_dataclass(cls, field_info: FieldInfo) -> bool:
        """True if field is an attrs dataclass"""
        if attr.has(field_info.field_type):
            return True

        return False

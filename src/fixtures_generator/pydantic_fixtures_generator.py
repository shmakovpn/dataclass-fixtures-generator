import typing
import pydantic
import pydantic_core
import inspect
from .dataclass_fixtures_generator import FieldInfo, DataclassFixturesGenerator

# noinspection SpellCheckingInspection
__all__ = (
    'IsNotPydanticError',
    'PydanticFixturesGenerator',
)


# noinspection SpellCheckingInspection
class IsNotPydanticError(TypeError):
    """
    Provided argument is not a pydantic model
    """
    pass


# noinspection SpellCheckingInspection
class PydanticFixturesGenerator(DataclassFixturesGenerator):
    @classmethod
    def _validate(cls, cls_: typing.Type) -> None:
        """validate that cls_ is pydantic model"""
        if not inspect.isclass(cls_):
            raise IsNotPydanticError(f'{cls_} is not a class')

        if not issubclass(cls_, pydantic.BaseModel):
            raise IsNotPydanticError(f'{cls_} is not a pydantic model')

    @classmethod
    def _get_fields(cls, cls_: typing.Type) -> typing.Tuple[FieldInfo, ...]:
        fields: typing.Dict[str, pydantic.fields.FieldInfo] = typing.cast(pydantic.BaseModel, cls_).model_fields

        field: pydantic.fields.FieldInfo
        field_name: str
        fields_info: typing.Tuple[FieldInfo, ...] = tuple(
            FieldInfo(
                field_name=field_name,
                field_type=typing.cast(type, field.annotation),
                default_value=field.default if field.default != pydantic_core.PydanticUndefined else None,
                default_factory=(
                    field.default_factory if field.default_factory != pydantic_core.PydanticUndefined else None
                ),
            ) for field_name, field in fields.items()
        )
        return fields_info

    @classmethod
    def _is_dataclass(cls, field_info: FieldInfo) -> bool:
        """True if field is a pydantic model """
        if not inspect.isclass(field_info.field_type):
            return False

        if issubclass(field_info.field_type, pydantic.BaseModel):
            return True

        return False

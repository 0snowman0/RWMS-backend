from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from Core.Domain.ViewModels.ValueObjects.Categories.dynamic_field_definition import DynamicFieldDefinition


class CreateCategoryDto(
    BaseModel,
):

    name: str

    description: str | None = None

    fields: list[
        DynamicFieldDefinition
    ] = Field(
        default_factory=list
    )
    
class CategoryDto(
    BaseModel,
):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int

    name: str

    description: str | None = None

    fields: list[
        DynamicFieldDefinition
    ] = Field(
        default_factory=list
    )

    created_at: datetime

    updated_at: datetime    
    
    
class UpdateCategoryDto(
    BaseModel,
):

    name: str

    description: str | None = None

    fields: list[
        DynamicFieldDefinition
    ] = Field(
        default_factory=list
    )    
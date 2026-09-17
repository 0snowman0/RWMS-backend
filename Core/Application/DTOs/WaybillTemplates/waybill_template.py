from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from Core.Domain.ViewModels.ValueObjects.Categories.dynamic_field_definition import (
    DynamicFieldDefinition,
)


class CreateWaybillTemplateDto(
    BaseModel,
):

    name: str

    description: str | None = None

    is_active: bool = True

    fields: list[
        DynamicFieldDefinition
    ] = Field(
        default_factory=list
    )


class UpdateWaybillTemplateDto(
    BaseModel,
):

    name: str

    description: str | None = None

    is_active: bool = True

    fields: list[
        DynamicFieldDefinition
    ] = Field(
        default_factory=list
    )


class WaybillTemplateDto(
    BaseModel,
):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int | None = None

    name: str

    description: str | None = None

    is_active: bool = True

    fields: list[
        DynamicFieldDefinition
    ] = Field(
        default_factory=list
    )

    created_at: datetime | None = None

    updated_at: datetime | None = None


class WaybillTemplateSummaryDto(
    BaseModel,
):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int | None = None

    name: str

    description: str | None = None

    is_active: bool = True

    created_at: datetime | None = None

    updated_at: datetime | None = None

from datetime import datetime
from typing import Any

from pydantic import (
    BaseModel,
    Field,
)

from Core.Domain.ViewModels.ValueObjects.Categories.dynamic_field_definition import (
    DynamicFieldDefinition,
)

from Core.Domain.ViewModels.ValueObjects.Products.product_attribute_value import (
    ProductAttributeValue,
)

class CreateProductDto(
    BaseModel,
):

    name: str

    category_ids: list[int] = Field(
        default_factory=list
    )

    attributes: list[
        ProductAttributeValue
    ] = Field(
        default_factory=list
    )

class UpdateProductDto(
    BaseModel,
):

    name: str

    category_ids: list[int] = Field(
        default_factory=list
    )

    attributes: list[
        ProductAttributeValue
    ] = Field(
        default_factory=list
    )

class ProductCategoryDto(
    BaseModel,
):

    id: int

    name: str

class ProductDynamicFieldDto(
    DynamicFieldDefinition,
):

    category_id: int

    category_name: str

    value: Any | None = None

class ProductDto(
    BaseModel,
):

    id: int

    name: str

    categories: list[
        ProductCategoryDto
    ] = Field(
        default_factory=list
    )

    fields: list[
        ProductDynamicFieldDto
    ] = Field(
        default_factory=list
    )

    created_at: datetime

    updated_at: datetime
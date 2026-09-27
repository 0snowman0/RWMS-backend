from Core.Application.DTOs.Products.product import (
    ProductCategoryDto,
    ProductDto,
    ProductDynamicFieldDto,
)
from Core.Domain.Models.Products.product import (
    Product,
)


def build_product_dto(
    product: Product,
) -> ProductDto:
    """
    Constructs a complete ProductDto combining category definitions,
    dynamic field values, and fixed fields.
    """
    category_dtos = [
        ProductCategoryDto(
            id=category.id,
            name=category.name,
        )
        for category in (product.categories or [])
    ]

    attribute_lookup = {
        (
            attribute.category_id,
            str(attribute.field_id),
        ): attribute
        for attribute in (product.attributes or [])
    }

    field_dtos: list[ProductDynamicFieldDto] = []

    for category in (product.categories or []):
        fields = sorted(
            [
                field
                for field in category.fields
                if field.is_active
            ],
            key=lambda field: field.sort_order,
        )

        for field in fields:
            key = (
                category.id,
                str(field.field_id),
            )
            attribute = attribute_lookup.get(key)

            if attribute is not None:
                value = attribute.value
            else:
                value = field.default_value

            field_data = field.model_dump(
                mode="python",
            )

            field_dto = ProductDynamicFieldDto(
                **field_data,
                category_id=category.id,
                category_name=category.name,
                value=value,
            )

            field_dtos.append(field_dto)

    return ProductDto(
        id=product.id,
        name=product.name,
        categories=category_dtos,
        fields=field_dtos,
        created_at=product.created_at,
        updated_at=product.updated_at,
    )

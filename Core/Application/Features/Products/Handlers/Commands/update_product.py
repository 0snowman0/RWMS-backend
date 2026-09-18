from Core.Application.Commons.base_response import (
    BaseResponse,
)

from Core.Application.Contracts.DataBases.UnitOfWorks.unit_of_works import (
    IUnitOfWork,
)

from Core.Application.Contracts.Mediators.mediator import (
    IRequestHandler,
)

from Core.Application.Features.Products.Requests.Commands.update_product import (
    UpdateProductCommand,
)

from Core.Application.Mediators.handler_decorators import (
    handler_for,
)

from Core.Domain.Models.Categories.category import (
    Category,
)

from Core.Domain.Models.Products.product import (
    Product,
)

from Core.Domain.ViewModels.ValueObjects.Products.product_attribute_value import (
    ProductAttributeValue,
)


@handler_for(UpdateProductCommand)
class UpdateProductCommandHandler(
    IRequestHandler[
        UpdateProductCommand,
        BaseResponse[Product],
    ]
):

    def __init__(
        self,
        uow: IUnitOfWork,
    ) -> None:

        self._uow = uow

    async def handle(
        self,
        request: UpdateProductCommand,
    ) -> BaseResponse[Product]:

        product = await self._uow.products.get(
            Product.id == request.product_id
        )

        if product is None:

            return BaseResponse[Product].not_found(
                message="Product not found.",
            )

        category_ids = list(
            dict.fromkeys(
                request.data.category_ids
            )
        )

        categories = await self._uow.categories.get_all(
            Category.id.in_(
                category_ids
            )
        )
        
        found_category_ids = {
            category.id
            for category in categories
        }

        missing_category_ids = [
            category_id
            for category_id in category_ids
            if category_id
            not in found_category_ids
        ]

        if missing_category_ids:

            raise ValueError(
                "One or more categories "
                "were not found: "
                f"{missing_category_ids}"
            )

        dynamic_fields = {}

        for category in categories:

            for field in category.fields:

                if not field.is_active:
                    continue

                key = (
                    category.id,
                    str(field.field_id),
                )

                dynamic_fields[
                    key
                ] = field

        attributes = list(
            request.data.attributes
        )

        attribute_keys = [
            (
                attribute.category_id,
                str(attribute.field_id),
            )
            for attribute in attributes
        ]

        if len(attribute_keys) != len(
            set(attribute_keys)
        ):

            raise ValueError(
                "Duplicate product attributes "
                "are not allowed."
            )

        for attribute in attributes:

            if attribute.category_id not in (
                found_category_ids
            ):

                raise ValueError(
                    "Attribute category does not "
                    "belong to the selected "
                    "product categories: "
                    f"{attribute.category_id}"
                )

        unknown_fields = []

        for attribute in attributes:

            key = (
                attribute.category_id,
                str(attribute.field_id),
            )

            if key not in dynamic_fields:

                unknown_fields.append(
                    {
                        "category_id": (
                            attribute.category_id
                        ),
                        "field_id": str(
                            attribute.field_id
                        ),
                    }
                )

        if unknown_fields:

            raise ValueError(
                "Product contains attributes "
                "that do not belong to the "
                "selected categories: "
                f"{unknown_fields}"
            )

        attribute_lookup = {
            (
                attribute.category_id,
                str(attribute.field_id),
            ): attribute
            for attribute in attributes
        }

        for (
            category_id,
            field_id,
        ), field in dynamic_fields.items():

            key = (
                category_id,
                field_id,
            )

            if key in attribute_lookup:
                continue

            if field.default_value is not None:

                default_attribute = (
                    ProductAttributeValue(
                        category_id=category_id,
                        field_id=field.field_id,
                        value=field.default_value,
                    )
                )

                attributes.append(
                    default_attribute
                )

                attribute_lookup[
                    key
                ] = default_attribute

                continue

            if field.required:

                raise ValueError(
                    f"Required field is missing: "
                    f"{field.title} "
                    f"({field.name})"
                )

        product.name = (
            request.data.name
        )

        product.categories = (
            categories
        )

        product.attributes = (
            attributes
        )

        return BaseResponse[Product].success(
            data=product,
            message="Product updated successfully.",
        )
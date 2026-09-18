from Core.Application.Commons.base_response import (
    BaseResponse,
)

from Core.Application.Contracts.DataBases.UnitOfWorks.unit_of_works import (
    IUnitOfWork,
)

from Core.Application.Contracts.Mediators.mediator import (
    IRequestHandler,
)

from Core.Application.DTOs.Products.product import (
    ProductCategoryDto,
    ProductDto,
    ProductDynamicFieldDto,
)

from Core.Application.Features.Products.Requests.Queries.get_product_by_id import (
    GetProductByIdQuery,
)

from Core.Application.Mediators.handler_decorators import (
    handler_for,
)

from Core.Domain.Models.Products.product import (
    Product,
)


@handler_for(GetProductByIdQuery)
class GetProductByIdQueryHandler(
    IRequestHandler[
        GetProductByIdQuery,
        BaseResponse[ProductDto],
    ]
):

    def __init__(
        self,
        uow: IUnitOfWork,
    ) -> None:

        self._uow = uow

    async def handle(
        self,
        request: GetProductByIdQuery,
    ) -> BaseResponse[ProductDto]:

        product = await self._uow.products.get(
            Product.id == request.product_id
        )

        if product is None:

            return BaseResponse[
                ProductDto
            ].not_found(
                message="Product not found.",
            )

        category_dtos = [
            ProductCategoryDto(
                id=category.id,
                name=category.name,
            )
            for category in product.categories
        ]

        attribute_lookup = {
            (
                attribute.category_id,
                str(attribute.field_id),
            ): attribute
            for attribute in product.attributes
        }

        field_dtos = []

        for category in product.categories:

            fields = sorted(
                [
                    field
                    for field in category.fields
                    if field.is_active
                ],
                key=lambda field: (
                    field.sort_order
                ),
            )

            for field in fields:

                key = (
                    category.id,
                    str(field.field_id),
                )

                attribute = (
                    attribute_lookup.get(
                        key
                    )
                )

                if attribute is not None:

                    value = (
                        attribute.value
                    )

                else:

                    value = (
                        field.default_value
                    )
                    
                field_data = (
                    field.model_dump(
                        mode="python",
                    )
                )

                field_dto = (
                    ProductDynamicFieldDto(
                        **field_data,
                        category_id=category.id,
                        category_name=category.name,
                        value=value,
                    )
                )

                field_dtos.append(
                    field_dto
                )

        product_dto = ProductDto(
            id=product.id,
            name=product.name,
            categories=category_dtos,
            fields=field_dtos,
            created_at=product.created_at,
            updated_at=product.updated_at,
        )

        return BaseResponse[
            ProductDto
        ].success(
            data=product_dto,
            message="Product retrieved successfully.",
        )
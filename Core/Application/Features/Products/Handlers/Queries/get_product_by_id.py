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
    ProductDto,
)
from Core.Application.Features.Products.Helpers.product_dto_builder import (
    build_product_dto,
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
            return BaseResponse[ProductDto].not_found(
                message="Product not found.",
            )

        product_dto = build_product_dto(product)

        return BaseResponse[ProductDto].success(
            data=product_dto,
            message="Product retrieved successfully.",
        )
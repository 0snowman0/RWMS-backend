from Core.Application.Commons.base_response import (
    BaseResponse,
)
from Core.Application.Contracts.DataBases.UnitOfWorks.unit_of_works import (
    IUnitOfWork,
)
from Core.Application.Contracts.Mediators.mediator import (
    IRequestHandler,
)
from Core.Application.DTOs.Common.pagination_dto import (
    PagedResultDto,
)
from Core.Application.DTOs.Products.product import (
    ProductDto,
)
from Core.Application.Features.Products.Helpers.product_dto_builder import (
    build_product_dto,
)
from Core.Application.Features.Products.Requests.Queries.get_paged_products import (
    GetPagedProductsQuery,
)
from Core.Application.Mediators.handler_decorators import (
    handler_for,
)


@handler_for(GetPagedProductsQuery)
class GetPagedProductsQueryHandler(
    IRequestHandler[
        GetPagedProductsQuery,
        BaseResponse[PagedResultDto[ProductDto]],
    ]
):

    def __init__(
        self,
        uow: IUnitOfWork,
    ) -> None:

        self._uow = uow

    async def handle(
        self,
        request: GetPagedProductsQuery,
    ) -> BaseResponse[PagedResultDto[ProductDto]]:

        paged_products = await self._uow.products.get_paged(
            pagination_params=request.pagination,
        )

        dtos = [
            build_product_dto(product)
            for product in paged_products.items
        ]

        paged_result = PagedResultDto[ProductDto].create(
            items=dtos,
            total_count=paged_products.total_count,
            page_number=paged_products.page_number,
            page_size=paged_products.page_size,
        )

        return BaseResponse[PagedResultDto[ProductDto]].success(
            data=paged_result,
            message="Products retrieved successfully.",
        )

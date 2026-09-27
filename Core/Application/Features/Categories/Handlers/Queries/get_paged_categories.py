from Core.Application.Commons.base_response import (
    BaseResponse,
)
from Core.Application.Contracts.DataBases.UnitOfWorks.unit_of_works import (
    IUnitOfWork,
)
from Core.Application.Contracts.Mapper.mapper import (
    IMapper,
)
from Core.Application.Contracts.Mediators.mediator import (
    IRequestHandler,
)
from Core.Application.DTOs.Categories.category import (
    CategorySummaryDto,
)
from Core.Application.DTOs.Common.pagination_dto import (
    PagedResultDto,
)
from Core.Application.Features.Categories.Requests.Queries.get_paged_categories import (
    GetPagedCategoriesQuery,
)
from Core.Application.Mediators.handler_decorators import (
    handler_for,
)


@handler_for(GetPagedCategoriesQuery)
class GetPagedCategoriesQueryHandler(
    IRequestHandler[
        GetPagedCategoriesQuery,
        BaseResponse[PagedResultDto[CategorySummaryDto]],
    ]
):

    def __init__(
        self,
        uow: IUnitOfWork,
        mapper: IMapper,
    ) -> None:

        self._uow = uow
        self._mapper = mapper

    async def handle(
        self,
        request: GetPagedCategoriesQuery,
    ) -> BaseResponse[PagedResultDto[CategorySummaryDto]]:

        paged_entities = await self._uow.categories.get_paged(
            pagination_params=request.pagination,
        )

        category_dtos = self._mapper.map_list(
            paged_entities.items,
            CategorySummaryDto,
        )

        paged_result = PagedResultDto[CategorySummaryDto].create(
            items=category_dtos,
            total_count=paged_entities.total_count,
            page_number=paged_entities.page_number,
            page_size=paged_entities.page_size,
        )

        return BaseResponse[PagedResultDto[CategorySummaryDto]].success(
            data=paged_result,
            message="Categories retrieved successfully.",
        )

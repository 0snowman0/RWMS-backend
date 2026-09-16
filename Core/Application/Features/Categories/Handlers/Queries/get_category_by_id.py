from Core.Application.Commons.base_response import (
    BaseResponse,
)

from Core.Application.Contracts.DataBases.UnitOfWorks.unit_of_works import (
    IUnitOfWork,
)

from Core.Application.Contracts.Mapper.mapper import IMapper
from Core.Application.Contracts.Mediators.mediator import (
    IRequestHandler,
)

from Core.Application.DTOs.Categories.category import (
    CategoryDto,
)

from Core.Application.Features.Categories.Requests.Queries.get_category_by_id import (
    GetCategoryByIdQuery,
)

from Core.Application.Mediators.handler_decorators import (
    handler_for,
)
from Core.Domain.Models.Categories.category import Category


@handler_for(GetCategoryByIdQuery)
class GetCategoryByIdQueryHandler(
    IRequestHandler[
        GetCategoryByIdQuery,
        BaseResponse[CategoryDto],
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
        request: GetCategoryByIdQuery,
    ) -> BaseResponse[CategoryDto]:

        category = await self._uow.categories.get(
            Category.id == request.category_id
        )

        if category is None:
            return BaseResponse[CategoryDto].not_found(
                message="Category not found.",
            )

        category_dto = self._mapper.map(
            category,
            CategoryDto,
        )
        
        return BaseResponse[CategoryDto].success(
            data=category_dto,
            message="Category retrieved successfully.",
        )
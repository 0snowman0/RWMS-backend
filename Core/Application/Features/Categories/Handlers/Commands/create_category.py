from Core.Application.Commons.base_response import (
    BaseResponse,
)

from Core.Application.Contracts.DataBases.UnitOfWorks.unit_of_works import (
    IUnitOfWork,
)

from Core.Application.Contracts.Mediators.mediator import (
    IRequestHandler,
)

from Core.Application.Features.Categories.Requests.Commands.create_category import (
    CreateCategoryCommand,
)

from Core.Application.Mediators.handler_decorators import (
    handler_for,
)

from Core.Domain.Models.Categories.category import (
    Category,
)


@handler_for(CreateCategoryCommand)
class CreateCategoryCommandHandler(
    IRequestHandler[
        CreateCategoryCommand,
        BaseResponse[Category],
    ]
):

    def __init__(
        self,
        uow: IUnitOfWork,
    ) -> None:

        self._uow = uow

    async def handle(
        self,
        request: CreateCategoryCommand,
    ) -> BaseResponse[Category]:

        category = Category(
            name=request.data.name,
            description=request.data.description,
        )

        category.fields = (
            request.data.fields
        )

        await self._uow.categories.add(
            category
        )

        return BaseResponse[Category].success(
            data=category,
            message="Category created successfully.",
        )
from Core.Application.Commons.base_response import (
    BaseResponse,
)

from Core.Application.Contracts.DataBases.UnitOfWorks.unit_of_works import (
    IUnitOfWork,
)

from Core.Application.Contracts.Mediators.mediator import (
    IRequestHandler,
)

from Core.Application.Features.Categories.Requests.Commands.update_category import (
    UpdateCategoryCommand,
)

from Core.Application.Mediators.handler_decorators import (
    handler_for,
)

from Core.Domain.Models.Categories.category import (
    Category,
)


@handler_for(UpdateCategoryCommand)
class UpdateCategoryCommandHandler(
    IRequestHandler[
        UpdateCategoryCommand,
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
        request: UpdateCategoryCommand,
    ) -> BaseResponse[Category]:

        category = await self._uow.categories.get(
            Category.id == request.category_id
        )

        if category is None:
            return BaseResponse[Category].not_found(
                message="Category not found.",
            )


        category.name = (
            request.data.name
        )

        category.description = (
            request.data.description
        )

        category.fields = (
            request.data.fields
        )


        return BaseResponse[Category].success(
            data=category,
            message="Category updated successfully.",
        )
from Core.Application.Commons.base_response import (
    BaseResponse,
)

from Core.Application.Contracts.DataBases.UnitOfWorks.unit_of_works import (
    IUnitOfWork,
)

from Core.Application.Contracts.Mediators.mediator import (
    IRequestHandler,
)

from Core.Application.Features.Categories.Requests.Commands.delete_category import (
    DeleteCategoryCommand,
)

from Core.Application.Mediators.handler_decorators import (
    handler_for,
)

from Core.Domain.Models.Categories.category import (
    Category,
)


@handler_for(DeleteCategoryCommand)
class DeleteCategoryCommandHandler(
    IRequestHandler[
        DeleteCategoryCommand,
        BaseResponse[bool],
    ]
):

    def __init__(
        self,
        uow: IUnitOfWork,
    ) -> None:

        self._uow = uow

    async def handle(
        self,
        request: DeleteCategoryCommand,
    ) -> BaseResponse[bool]:

        category = await self._uow.categories.get(
            Category.id == request.category_id
        )

        if category is None:

            return BaseResponse[bool].not_found(
                message="Category not found.",
            )

        await self._uow.categories.delete(
            category
        )

        return BaseResponse[bool].success(
            data=True,
            message="Category deleted successfully.",
        )
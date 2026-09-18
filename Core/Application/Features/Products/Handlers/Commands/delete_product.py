from Core.Application.Commons.base_response import (
    BaseResponse,
)

from Core.Application.Contracts.DataBases.UnitOfWorks.unit_of_works import (
    IUnitOfWork,
)

from Core.Application.Contracts.Mediators.mediator import (
    IRequestHandler,
)

from Core.Application.Features.Products.Requests.Commands.delete_product import (
    DeleteProductCommand,
)

from Core.Application.Mediators.handler_decorators import (
    handler_for,
)

from Core.Domain.Models.Products.product import (
    Product,
)


@handler_for(DeleteProductCommand)
class DeleteProductCommandHandler(
    IRequestHandler[
        DeleteProductCommand,
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
        request: DeleteProductCommand,
    ) -> BaseResponse[bool]:

        product = await self._uow.products.get(
            Product.id == request.product_id
        )

        if product is None:

            return BaseResponse[bool].not_found(
                message="Product not found.",
            )

        await self._uow.products.delete(
            product
        )

        return BaseResponse[bool].success(
            data=True,
            message="Product deleted successfully.",
        )
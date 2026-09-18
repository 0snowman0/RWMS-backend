from Core.Application.Commons.base_response import (
    BaseResponse,
)
from Core.Application.Contracts.DataBases.UnitOfWorks.unit_of_works import (
    IUnitOfWork,
)
from Core.Application.Contracts.Mediators.mediator import (
    IRequestHandler,
)
from Core.Application.Features.WaybillTemplates.Requests.Commands.delete_waybill_template import (
    DeleteWaybillTemplateCommand,
)
from Core.Application.Mediators.handler_decorators import (
    handler_for,
)
from Core.Domain.Models.WaybillTemplates.waybill_template import (
    WaybillTemplate,
)


@handler_for(DeleteWaybillTemplateCommand)
class DeleteWaybillTemplateCommandHandler(
    IRequestHandler[
        DeleteWaybillTemplateCommand,
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
        request: DeleteWaybillTemplateCommand,
    ) -> BaseResponse[bool]:

        template = await self._uow.waybill_templates.get(
            WaybillTemplate.id == request.template_id
        )

        if template is None:
            return BaseResponse[bool].not_found(
                message="Waybill template not found.",
            )

        await self._uow.waybill_templates.delete(
            template
        )

        return BaseResponse[bool].success(
            data=True,
            message="Waybill template deleted successfully.",
        )

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
from Core.Application.DTOs.WaybillTemplates.waybill_template import (
    WaybillTemplateDto,
)
from Core.Application.Features.WaybillTemplates.Requests.Commands.update_waybill_template import (
    UpdateWaybillTemplateCommand,
)
from Core.Application.Mediators.handler_decorators import (
    handler_for,
)
from Core.Domain.Models.WaybillTemplates.waybill_template import (
    WaybillTemplate,
)


@handler_for(UpdateWaybillTemplateCommand)
class UpdateWaybillTemplateCommandHandler(
    IRequestHandler[
        UpdateWaybillTemplateCommand,
        BaseResponse[WaybillTemplateDto],
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
        request: UpdateWaybillTemplateCommand,
    ) -> BaseResponse[WaybillTemplateDto]:

        template = await self._uow.waybill_templates.get(
            WaybillTemplate.id == request.template_id
        )

        if template is None:
            return BaseResponse[WaybillTemplateDto].not_found(
                message="Waybill template not found.",
            )

        if template.name != request.data.name:
            existing = await self._uow.waybill_templates.get_by_name(
                request.data.name
            )
            if existing is not None:
                return BaseResponse[WaybillTemplateDto].conflict(
                    message="Waybill template with this name already exists.",
                )

        template.name = (
            request.data.name
        )
        template.description = (
            request.data.description
        )
        template.is_active = (
            request.data.is_active
        )
        template.fields = (
            request.data.fields
        )

        template_dto = self._mapper.map(
            template,
            WaybillTemplateDto,
        )

        return BaseResponse[WaybillTemplateDto].success(
            data=template_dto,
            message="Waybill template updated successfully.",
        )

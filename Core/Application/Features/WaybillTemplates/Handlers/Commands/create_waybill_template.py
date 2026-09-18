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
from Core.Application.Features.WaybillTemplates.Requests.Commands.create_waybill_template import (
    CreateWaybillTemplateCommand,
)
from Core.Application.Mediators.handler_decorators import (
    handler_for,
)
from Core.Domain.Models.WaybillTemplates.waybill_template import (
    WaybillTemplate,
)


@handler_for(CreateWaybillTemplateCommand)
class CreateWaybillTemplateCommandHandler(
    IRequestHandler[
        CreateWaybillTemplateCommand,
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
        request: CreateWaybillTemplateCommand,
    ) -> BaseResponse[WaybillTemplateDto]:

        existing = await self._uow.waybill_templates.get_by_name(
            request.data.name
        )

        if existing is not None:
            return BaseResponse[WaybillTemplateDto].conflict(
                message="Waybill template with this name already exists.",
            )

        template = WaybillTemplate(
            name=request.data.name,
            description=request.data.description,
            is_active=request.data.is_active,
        )

        template.fields = (
            request.data.fields
        )

        await self._uow.waybill_templates.add(
            template
        )

        template_dto = self._mapper.map(
            template,
            WaybillTemplateDto,
        )

        return BaseResponse[WaybillTemplateDto].success(
            data=template_dto,
            message="Waybill template created successfully.",
        )

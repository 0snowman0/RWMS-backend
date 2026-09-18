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
from Core.Application.DTOs.Waybills.waybill import (
    WaybillDto,
)
from Core.Application.Features.Waybills.Helpers.waybill_dto_builder import (
    build_waybill_dto,
)
from Core.Application.Features.Waybills.Requests.Commands.update_waybill import (
    UpdateWaybillCommand,
)
from Core.Application.Features.Waybills.Validators.dynamic_field_validator import (
    validate_waybill_attributes,
)
from Core.Application.Mediators.handler_decorators import (
    handler_for,
)
from Core.Domain.Models.WaybillTemplates.waybill_template import (
    WaybillTemplate,
)
from Core.Domain.Models.Waybills.waybill import (
    Waybill,
)


@handler_for(UpdateWaybillCommand)
class UpdateWaybillCommandHandler(
    IRequestHandler[
        UpdateWaybillCommand,
        BaseResponse[WaybillDto],
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
        request: UpdateWaybillCommand,
    ) -> BaseResponse[WaybillDto]:

        waybill = await self._uow.waybills.get(
            Waybill.id == request.waybill_id
        )

        if waybill is None:
            return BaseResponse[WaybillDto].not_found(
                message="Waybill not found.",
            )

        # Template resolution
        target_template_id = request.data.template_id or waybill.template_id
        template = await self._uow.waybill_templates.get(
            WaybillTemplate.id == target_template_id
        )

        if template is None:
            return BaseResponse[WaybillDto].not_found(
                message="Waybill template not found.",
            )

        # Dynamic attributes validation
        attributes = request.data.attributes
        if attributes:
            errors, final_attributes = validate_waybill_attributes(
                attributes=attributes,
                schema=template.fields,
                check_required=False,
            )
            if errors:
                return BaseResponse[WaybillDto].validation_error(
                    message="Dynamic attributes validation failed.",
                    errors=errors,
                )
            waybill.attributes = final_attributes

        # Check waybill_number uniqueness if changed
        if request.data.waybill_number and request.data.waybill_number != waybill.waybill_number:
            existing = await self._uow.waybills.get_by_waybill_number(
                request.data.waybill_number
            )
            if existing is not None:
                return BaseResponse[WaybillDto].conflict(
                    message="Waybill with this number already exists.",
                )

        # Map fixed fields using AutoMapper
        self._mapper.map_to(
            request.data,
            waybill,
            ignore_none=True,
        )

        waybill.template = template
        waybill.template_id = target_template_id

        waybill_dto = build_waybill_dto(waybill)

        return BaseResponse[WaybillDto].success(
            data=waybill_dto,
            message="Waybill updated successfully.",
        )

from Core.Application.Commons.base_response import (
    BaseResponse,
)
from Core.Application.Contracts.DataBases.UnitOfWorks.unit_of_works import (
    IUnitOfWork,
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
from Core.Application.Features.Waybills.Requests.Commands.create_waybill import (
    CreateWaybillCommand,
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


@handler_for(CreateWaybillCommand)
class CreateWaybillCommandHandler(
    IRequestHandler[
        CreateWaybillCommand,
        BaseResponse[WaybillDto],
    ]
):

    def __init__(
        self,
        uow: IUnitOfWork,
    ) -> None:

        self._uow = uow

    async def handle(
        self,
        request: CreateWaybillCommand,
    ) -> BaseResponse[WaybillDto]:

        # 1. Validate template exists and is active
        template = await self._uow.waybill_templates.get(
            WaybillTemplate.id == request.data.template_id
        )

        if template is None:
            return BaseResponse[WaybillDto].not_found(
                message="Waybill template not found.",
            )

        if not template.is_active:
            return BaseResponse[WaybillDto].validation_error(
                message="Waybill template is not active.",
            )

        # 2. Check waybill_number uniqueness if provided
        if request.data.waybill_number:
            existing = await self._uow.waybills.get_by_waybill_number(
                request.data.waybill_number
            )
            if existing is not None:
                return BaseResponse[WaybillDto].conflict(
                    message="Waybill with this number already exists.",
                )

        # 3. Validate attributes if provided (required fields not enforced in initial creation if draft)
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
            attributes = final_attributes

        # 4. Create Waybill entity
        waybill = Waybill(
            name=request.data.name,
            template_id=request.data.template_id,
            waybill_number=request.data.waybill_number,
            waybill_date=request.data.waybill_date,
            received_date=request.data.received_date,
            sender_name=request.data.sender_name,
            sender_contact=request.data.sender_contact,
            receiver_name=request.data.receiver_name,
            receiver_contact=request.data.receiver_contact,
            origin=request.data.origin,
            destination=request.data.destination,
            vehicle_type=request.data.vehicle_type,
            vehicle_number=request.data.vehicle_number,
            driver_name=request.data.driver_name,
            driver_contact=request.data.driver_contact,
            total_weight=request.data.total_weight,
            priority=request.data.priority,
            description=request.data.description,
            internal_notes=request.data.internal_notes,
        )

        waybill.attributes = attributes
        waybill.template = template

        await self._uow.waybills.add(
            waybill
        )

        waybill_dto = build_waybill_dto(waybill)

        return BaseResponse[WaybillDto].success(
            data=waybill_dto,
            message="Waybill created successfully.",
        )

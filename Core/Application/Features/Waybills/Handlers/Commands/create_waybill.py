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
from Core.Application.Features.Waybills.Requests.Commands.create_waybill import (
    CreateWaybillCommand,
)
from Core.Application.Features.Waybills.Validators.dynamic_field_validator import (
    validate_dynamic_fields,
)
from Core.Application.Mediators.handler_decorators import (
    handler_for,
)
from Core.Domain.Enums.Waybills.waybill_status import (
    WaybillStatus,
)
from Core.Domain.Models.WaybillTemplates.waybill_template import (
    WaybillTemplate,
)
from Core.Domain.Models.Waybills.waybill import (
    Waybill,
)
from Core.Domain.Models.Waybills.waybill_item import (
    WaybillItem,
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
        mapper: IMapper,
    ) -> None:

        self._uow = uow
        self._mapper = mapper

    async def handle(
        self,
        request: CreateWaybillCommand,
    ) -> BaseResponse[WaybillDto]:

        # 1. Validate waybill_number uniqueness
        existing = await self._uow.waybills.get_by_waybill_number(
            request.data.waybill_number
        )

        if existing is not None:
            return BaseResponse[WaybillDto].conflict(
                message="Waybill with this number already exists.",
            )

        # 2. Validate template exists and is active
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

        # 3. Validate dynamic fields against template schema
        errors = validate_dynamic_fields(
            request.data.dynamic_fields,
            template.fields,
        )

        if errors:
            return BaseResponse[WaybillDto].validation_error(
                message="Dynamic field validation failed.",
                errors=errors,
            )

        # 4. Business rules
        if request.data.origin == request.data.destination:
            return BaseResponse[WaybillDto].validation_error(
                message="Origin and destination cannot be the same.",
            )

        if not request.data.items:
            return BaseResponse[WaybillDto].validation_error(
                message="At least one waybill item is required.",
            )

        # 5. Create Waybill entity
        waybill = Waybill(
            waybill_number=request.data.waybill_number,
            template_id=request.data.template_id,
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
            total_items_count=request.data.total_items_count,
            total_weight=request.data.total_weight,
            status=WaybillStatus.REGISTERED.value,
            priority=request.data.priority,
            description=request.data.description,
            internal_notes=request.data.internal_notes,
        )

        waybill.dynamic_fields = (
            request.data.dynamic_fields
        )

        # 6. Create WaybillItem entities
        for item_dto in request.data.items:
            waybill.items.append(
                WaybillItem(
                    item_id=item_dto.item_id,
                    item_name=item_dto.item_name,
                    quantity_sent=item_dto.quantity_sent,
                    quantity_received=item_dto.quantity_received,
                    batch_number=item_dto.batch_number,
                    manufacturing_date=item_dto.manufacturing_date,
                    expiry_date=item_dto.expiry_date,
                    quality_status=item_dto.quality_status,
                    notes=item_dto.notes,
                )
            )

        await self._uow.waybills.add(
            waybill
        )

        waybill_dto = self._mapper.map(
            waybill,
            WaybillDto,
        )

        return BaseResponse[WaybillDto].success(
            data=waybill_dto,
            message="Waybill created successfully.",
        )

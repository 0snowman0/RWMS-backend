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
from Core.Application.Features.Waybills.Requests.Commands.update_waybill import (
    UpdateWaybillCommand,
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

        # Cancelled waybill cannot be edited
        if waybill.status == WaybillStatus.CANCELLED.value:
            return BaseResponse[WaybillDto].validation_error(
                message="Cancelled waybill cannot be edited.",
            )

        # Template validation
        template = await self._uow.waybill_templates.get(
            WaybillTemplate.id == waybill.template_id
        )

        if template is not None:
            errors = validate_dynamic_fields(
                request.data.dynamic_fields,
                template.fields,
            )
            if errors:
                return BaseResponse[WaybillDto].validation_error(
                    message="Dynamic field validation failed.",
                    errors=errors,
                )

        # Business rules
        if request.data.origin == request.data.destination:
            return BaseResponse[WaybillDto].validation_error(
                message="Origin and destination cannot be the same.",
            )

        if not request.data.items:
            return BaseResponse[WaybillDto].validation_error(
                message="At least one waybill item is required.",
            )

        # Update waybill fields
        waybill.waybill_date = (
            request.data.waybill_date
        )
        waybill.received_date = (
            request.data.received_date
        )
        waybill.sender_name = (
            request.data.sender_name
        )
        waybill.sender_contact = (
            request.data.sender_contact
        )
        waybill.receiver_name = (
            request.data.receiver_name
        )
        waybill.receiver_contact = (
            request.data.receiver_contact
        )
        waybill.origin = (
            request.data.origin
        )
        waybill.destination = (
            request.data.destination
        )
        waybill.vehicle_type = (
            request.data.vehicle_type
        )
        waybill.vehicle_number = (
            request.data.vehicle_number
        )
        waybill.driver_name = (
            request.data.driver_name
        )
        waybill.driver_contact = (
            request.data.driver_contact
        )
        waybill.total_items_count = (
            request.data.total_items_count
        )
        waybill.total_weight = (
            request.data.total_weight
        )
        waybill.priority = (
            request.data.priority
        )
        waybill.description = (
            request.data.description
        )
        waybill.internal_notes = (
            request.data.internal_notes
        )
        waybill.dynamic_fields = (
            request.data.dynamic_fields
        )

        # Replace items
        waybill.items.clear()
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

        waybill_dto = self._mapper.map(
            waybill,
            WaybillDto,
        )

        return BaseResponse[WaybillDto].success(
            data=waybill_dto,
            message="Waybill updated successfully.",
        )

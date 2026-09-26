from Core.Application.DTOs.Waybills.waybill import (
    WaybillDto,
    WaybillDynamicFieldDto,
    WaybillTemplateReferenceDto,
)
from Core.Domain.Models.Waybills.waybill import (
    Waybill,
)


def build_waybill_dto(
    waybill: Waybill,
) -> WaybillDto:
    """
    Constructs a complete WaybillDto combining template definitions,
    dynamic field values, and fixed fields.
    """
    template_dto = None
    field_dtos: list[WaybillDynamicFieldDto] = []

    if waybill.template is not None:
        template_dto = WaybillTemplateReferenceDto(
            id=waybill.template.id,
            name=waybill.template.name,
        )

        attr_lookup = {
            str(attr.field_id): attr
            for attr in waybill.attributes
        }

        sorted_fields = sorted(
            [
                f
                for f in waybill.template.fields
                if f.is_active
            ],
            key=lambda f: f.sort_order,
        )

        for field in sorted_fields:
            attr = attr_lookup.get(str(field.field_id))
            if attr is not None:
                value = attr.value
            else:
                value = field.default_value

            field_data = field.model_dump(
                mode="python",
            )

            field_dto = WaybillDynamicFieldDto(
                **field_data,
                template_id=waybill.template.id,
                template_name=waybill.template.name,
                value=value,
            )

            field_dtos.append(field_dto)

    return WaybillDto(
        id=waybill.id,
        name=waybill.name,
        waybill_number=waybill.waybill_number,
        template_id=waybill.template_id,
        template=template_dto,
        status=waybill.status,
        priority=waybill.priority,
        waybill_date=waybill.waybill_date,
        received_date=waybill.received_date,
        sender_name=waybill.sender_name,
        sender_contact=waybill.sender_contact,
        receiver_name=waybill.receiver_name,
        receiver_contact=waybill.receiver_contact,
        origin=waybill.origin,
        destination=waybill.destination,
        vehicle_type=waybill.vehicle_type,
        vehicle_number=waybill.vehicle_number,
        driver_name=waybill.driver_name,
        driver_contact=waybill.driver_contact,
        total_weight=waybill.total_weight,
        description=waybill.description,
        internal_notes=waybill.internal_notes,
        fields=field_dtos,
        created_by=waybill.created_by,
        created_at=waybill.created_at,
        updated_at=waybill.updated_at,
    )

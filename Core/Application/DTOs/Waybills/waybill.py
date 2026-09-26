from datetime import date, datetime
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from Core.Domain.Enums.Waybills.waybill_priority import (
    WaybillPriority,
)
from Core.Domain.Enums.Waybills.waybill_status import (
    WaybillStatus,
)
from Core.Domain.ViewModels.ValueObjects.Categories.dynamic_field_definition import (
    DynamicFieldDefinition,
)
from Core.Domain.ViewModels.ValueObjects.Waybills.waybill_attribute_value import (
    WaybillAttributeValue,
)


# =========================================================
# Template Reference & Dynamic Field DTOs
# =========================================================


class WaybillTemplateReferenceDto(
    BaseModel,
):
    id: int
    name: str


class WaybillDynamicFieldDto(
    DynamicFieldDefinition,
):
    template_id: int
    template_name: str
    value: Any | None = None


# =========================================================
# Input DTOs
# =========================================================


class CreateWaybillDto(
    BaseModel,
):
    """Creation of waybill: requires name and template_id; other fields optional"""
    name: str
    template_id: int
    waybill_number: str | None = None
    waybill_date: date | None = None
    received_date: date | None = None
    sender_name: str | None = None
    sender_contact: str | None = None
    receiver_name: str | None = None
    receiver_contact: str | None = None
    origin: str | None = None
    destination: str | None = None
    vehicle_type: str | None = None
    vehicle_number: str | None = None
    driver_name: str | None = None
    driver_contact: str | None = None
    total_weight: float | None = None
    priority: str = WaybillPriority.NORMAL.value
    status: str = WaybillStatus.REGISTERED.value
    description: str | None = None
    internal_notes: str | None = None
    attributes: list[WaybillAttributeValue] = Field(
        default_factory=list,
    )


class UpdateWaybillDto(
    BaseModel,
):
    """Full update or completion of waybill data"""
    name: str
    template_id: int | None = None
    waybill_number: str | None = None
    waybill_date: date | None = None
    received_date: date | None = None
    sender_name: str | None = None
    sender_contact: str | None = None
    receiver_name: str | None = None
    receiver_contact: str | None = None
    origin: str | None = None
    destination: str | None = None
    vehicle_type: str | None = None
    vehicle_number: str | None = None
    driver_name: str | None = None
    driver_contact: str | None = None
    total_weight: float | None = None
    priority: str = WaybillPriority.NORMAL.value
    status: str | None = None
    description: str | None = None
    internal_notes: str | None = None
    attributes: list[WaybillAttributeValue] = Field(
        default_factory=list,
    )


# =========================================================
# Output DTOs
# =========================================================


class WaybillDto(
    BaseModel,
):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int | None = None
    name: str
    waybill_number: str | None = None
    template_id: int
    template: WaybillTemplateReferenceDto | None = None
    priority: str = WaybillPriority.NORMAL.value
    status: str = WaybillStatus.REGISTERED.value
    waybill_date: date | None = None
    received_date: date | None = None
    sender_name: str | None = None
    sender_contact: str | None = None
    receiver_name: str | None = None
    receiver_contact: str | None = None
    origin: str | None = None
    destination: str | None = None
    vehicle_type: str | None = None
    vehicle_number: str | None = None
    driver_name: str | None = None
    driver_contact: str | None = None
    total_weight: float | None = None
    description: str | None = None
    internal_notes: str | None = None
    fields: list[WaybillDynamicFieldDto] = Field(
        default_factory=list,
    )
    created_by: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class WaybillSummaryDto(
    BaseModel,
):
    """Lightweight DTO for list endpoints"""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int | None = None
    name: str
    waybill_number: str | None = None
    template_id: int
    waybill_date: date | None = None
    sender_name: str | None = None
    receiver_name: str | None = None
    origin: str | None = None
    destination: str | None = None
    priority: str
    status: str
    created_at: datetime | None = None

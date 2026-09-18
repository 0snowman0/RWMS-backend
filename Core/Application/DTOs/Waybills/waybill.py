from datetime import date, datetime
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from Core.Domain.Enums.Waybills.quality_status import (
    QualityStatus,
)
from Core.Domain.Enums.Waybills.waybill_priority import (
    WaybillPriority,
)
from Core.Domain.Enums.Waybills.waybill_status import (
    WaybillStatus,
)


# =========================================================
# Input DTOs
# =========================================================


class WaybillItemInputDto(
    BaseModel,
):
    item_id: int | None = None
    item_name: str
    quantity_sent: int
    quantity_received: int | None = None
    batch_number: str | None = None
    manufacturing_date: date | None = None
    expiry_date: date | None = None
    quality_status: str = QualityStatus.GOOD.value
    notes: str | None = None


class CreateWaybillDto(
    BaseModel,
):
    waybill_number: str
    template_id: int
    waybill_date: date
    received_date: date | None = None
    sender_name: str
    sender_contact: str | None = None
    receiver_name: str
    receiver_contact: str | None = None
    origin: str
    destination: str
    vehicle_type: str | None = None
    vehicle_number: str | None = None
    driver_name: str | None = None
    driver_contact: str | None = None
    total_items_count: int | None = None
    total_weight: float | None = None
    priority: str = WaybillPriority.NORMAL.value
    description: str | None = None
    internal_notes: str | None = None
    dynamic_fields: dict[str, Any] = Field(
        default_factory=dict,
    )
    items: list[WaybillItemInputDto] = Field(
        default_factory=list,
    )


class UpdateWaybillDto(
    BaseModel,
):
    # template_id and waybill_number are immutable
    waybill_date: date
    received_date: date | None = None
    sender_name: str
    sender_contact: str | None = None
    receiver_name: str
    receiver_contact: str | None = None
    origin: str
    destination: str
    vehicle_type: str | None = None
    vehicle_number: str | None = None
    driver_name: str | None = None
    driver_contact: str | None = None
    total_items_count: int | None = None
    total_weight: float | None = None
    priority: str = WaybillPriority.NORMAL.value
    description: str | None = None
    internal_notes: str | None = None
    dynamic_fields: dict[str, Any] = Field(
        default_factory=dict,
    )
    items: list[WaybillItemInputDto] = Field(
        default_factory=list,
    )


class UpdateWaybillStatusDto(
    BaseModel,
):
    status: str


# =========================================================
# Output DTOs
# =========================================================


class WaybillItemDto(
    BaseModel,
):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int | None = None
    item_id: int | None = None
    item_name: str
    quantity_sent: int
    quantity_received: int | None = None
    batch_number: str | None = None
    manufacturing_date: date | None = None
    expiry_date: date | None = None
    quality_status: str = QualityStatus.GOOD.value
    notes: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class WaybillDto(
    BaseModel,
):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int | None = None
    waybill_number: str
    template_id: int
    waybill_date: date
    received_date: date | None = None
    sender_name: str
    sender_contact: str | None = None
    receiver_name: str
    receiver_contact: str | None = None
    origin: str
    destination: str
    vehicle_type: str | None = None
    vehicle_number: str | None = None
    driver_name: str | None = None
    driver_contact: str | None = None
    total_items_count: int | None = None
    total_weight: float | None = None
    status: str = WaybillStatus.REGISTERED.value
    priority: str = WaybillPriority.NORMAL.value
    description: str | None = None
    internal_notes: str | None = None
    dynamic_fields: dict[str, Any] = Field(
        default_factory=dict,
    )
    items: list[WaybillItemDto] = Field(
        default_factory=list,
    )
    created_by: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class WaybillSummaryDto(
    BaseModel,
):
    """Lightweight DTO for list endpoints — no items or dynamic_fields"""

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int | None = None
    waybill_number: str
    template_id: int
    waybill_date: date
    sender_name: str
    receiver_name: str
    origin: str
    destination: str
    status: str
    priority: str
    total_items_count: int | None = None
    created_at: datetime | None = None

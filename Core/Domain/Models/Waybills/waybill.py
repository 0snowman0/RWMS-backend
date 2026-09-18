from datetime import date
from typing import Any

from sqlalchemy import (
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import (
    JSONB,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from Core.Domain.Enums.Waybills.waybill_priority import (
    WaybillPriority,
)
from Core.Domain.Enums.Waybills.waybill_status import (
    WaybillStatus,
)
from Core.Domain.Models.Base.base_models import (
    Base,
)
from Core.Domain.Models.WaybillTemplates.waybill_template import (
    WaybillTemplate,
)
from Core.Domain.Models.Waybills.waybill_item import (
    WaybillItem,
)


class Waybill(Base):

    # =========================================================
    # Identity
    # =========================================================

    waybill_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    # =========================================================
    # Template Reference
    # =========================================================

    template_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("waybilltemplates.id"),
        nullable=False,
    )

    # =========================================================
    # Dates
    # =========================================================

    waybill_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    received_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    # =========================================================
    # Sender
    # =========================================================

    sender_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    sender_contact: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # =========================================================
    # Receiver
    # =========================================================

    receiver_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    receiver_contact: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # =========================================================
    # Location
    # =========================================================

    origin: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    destination: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # =========================================================
    # Vehicle & Driver
    # =========================================================

    vehicle_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    vehicle_number: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    driver_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    driver_contact: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    # =========================================================
    # Totals
    # =========================================================

    total_items_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    total_weight: Mapped[float | None] = mapped_column(
        Numeric(12, 3),
        nullable=True,
    )

    # =========================================================
    # Status & Priority
    # =========================================================

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default=WaybillStatus.REGISTERED.value,
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=WaybillPriority.NORMAL.value,
    )

    # =========================================================
    # Text Fields
    # =========================================================

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    internal_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # =========================================================
    # Dynamic Fields (values, not schema)
    # =========================================================

    _dynamic_fields: Mapped[
        dict[str, Any]
    ] = mapped_column(
        "dynamic_fields",
        JSONB,
        nullable=False,
        default=dict,
    )

    @property
    def dynamic_fields(
        self,
    ) -> dict[str, Any]:
        if not self._dynamic_fields:
            return {}
        return self._dynamic_fields

    @dynamic_fields.setter
    def dynamic_fields(
        self,
        value: dict[str, Any],
    ) -> None:
        self._dynamic_fields = value or {}

    # =========================================================
    # Audit
    # =========================================================

    created_by: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # =========================================================
    # Relationships
    # =========================================================

    template: Mapped[WaybillTemplate] = relationship(
        "WaybillTemplate",
        lazy="joined",
    )

    items: Mapped[list[WaybillItem]] = relationship(
        "WaybillItem",
        back_populates="waybill",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

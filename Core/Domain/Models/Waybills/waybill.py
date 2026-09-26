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
from Core.Domain.ViewModels.ValueObjects.Waybills.waybill_attribute_value import (
    WaybillAttributeValue,
)


class Waybill(Base):

    # =========================================================
    # Basic / Identity
    # =========================================================

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    waybill_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
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

    waybill_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    received_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    # =========================================================
    # Sender
    # =========================================================

    sender_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    sender_contact: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # =========================================================
    # Receiver
    # =========================================================

    receiver_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    receiver_contact: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # =========================================================
    # Location
    # =========================================================

    origin: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    destination: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
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
    # Dynamic Attributes (stored as JSONB list of values)
    # =========================================================

    _attributes: Mapped[
        list[dict[str, Any]]
    ] = mapped_column(
        "attributes",
        JSONB,
        nullable=False,
        default=list,
    )

    @property
    def attributes(
        self,
    ) -> list[
        WaybillAttributeValue
    ]:
        if not self._attributes:
            return []

        return [
            WaybillAttributeValue.model_validate(
                item
            )
            for item in self._attributes
        ]

    @attributes.setter
    def attributes(
        self,
        value: list[
            WaybillAttributeValue
        ],
    ) -> None:
        self._attributes = [
            item.model_dump(
                mode="json",
            )
            for item in value
        ]

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

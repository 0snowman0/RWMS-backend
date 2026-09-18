from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import (
    Date,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from Core.Domain.Enums.Waybills.quality_status import (
    QualityStatus,
)
from Core.Domain.Models.Base.base_models import (
    Base,
)

if TYPE_CHECKING:
    from Core.Domain.Models.Waybills.waybill import Waybill


class WaybillItem(Base):

    waybill_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "waybills.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    item_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    item_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    quantity_sent: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    quantity_received: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    batch_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    manufacturing_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    expiry_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    quality_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=QualityStatus.GOOD.value,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # =========================================================
    # Relationships
    # =========================================================

    waybill: Mapped["Waybill"] = relationship(
        "Waybill",
        back_populates="items",
    )

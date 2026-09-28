from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    BigInteger,
    DateTime,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from Infrastructure.Persistence.Configs.PGdatabase import (
    Base,
)


class AuditLog(Base):
    """
    موجودیت مستقل برای ثبت وقایع ممیزی تغییرات پایگاه داده (Audit Log).
    نام جدول: audit_logs
    """

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    table_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    old_values: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    new_values: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    primary_key: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )

    user_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )

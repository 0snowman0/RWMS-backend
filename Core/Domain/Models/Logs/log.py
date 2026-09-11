from typing import Any

from sqlalchemy import (
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from Infrastructure.Persistence.Configs.PGdatabase import (
    Base,
)


class Log(Base):

    # سطح لاگ
    # DEBUG=10, INFO=20, WARNING=30, ERROR=40, CRITICAL=50
    level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    # متن اصلی لاگ
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    # شناسه همین HTTP Request
    request_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    # شناسه ارتباط چند عملیات مرتبط
    correlation_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    # IP درخواست‌کننده
    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )

    # بعداً بعد از تکمیل Authentication استفاده می‌کنیم
    user_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )

    # HTTP Context
    http_method: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    status_code: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # منبع ایجاد Log
    logger_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Exception
    exception_type: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    exception_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    stack_trace: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # اطلاعات آزاد و توسعه‌پذیر
    properties: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class AuditLogEntry:
    """
    نمای داده‌ای رکورد ممیزی برای انتقال سریع در صف درون‌حافظه‌ای.
    """

    table_name: str
    action: str
    primary_key: dict[str, Any]
    old_values: dict[str, Any] | None = None
    new_values: dict[str, Any] | None = None
    user_id: int | None = None
    created_at: datetime | None = None

from datetime import datetime
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
)


class AuditLogDto(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    table_name: str
    action: str
    old_values: dict[str, Any] | None = None
    new_values: dict[str, Any] | None = None
    primary_key: dict[str, Any]
    user_id: int | None = None
    created_at: datetime
    updated_at: datetime | None = None

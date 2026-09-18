from typing import Any
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
)


class WaybillAttributeValue(
    BaseModel,
):

    model_config = ConfigDict(
        validate_assignment=True,
    )

    template_id: int | None = None

    field_id: UUID

    value: Any | None = None

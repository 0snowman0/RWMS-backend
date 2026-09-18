from typing import Any
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
)


class ProductAttributeValue(
    BaseModel,
):

    model_config = ConfigDict(
        validate_assignment=True,
    )

    category_id: int

    field_id: UUID

    value: Any | None = None

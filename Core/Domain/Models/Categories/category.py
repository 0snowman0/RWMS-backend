from typing import Any

from sqlalchemy import (
    String,
    Text,
)

from sqlalchemy.dialects.postgresql import (
    JSONB,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from Core.Domain.Models.Base.base_models import (
    Base,
)
from Core.Domain.ViewModels.ValueObjects.Categories.dynamic_field_definition import DynamicFieldDefinition




class Category(
    Base,
):

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # =========================================================
    # Raw JSON Storage
    # =========================================================

    _fields_schema: Mapped[
        list[dict[str, Any]]
    ] = mapped_column(
        "fields_schema",
        JSONB,
        nullable=False,
        default=list,
    )

    # =========================================================
    # Dynamic Fields
    # =========================================================

    @property
    def fields(
        self,
    ) -> list[
        DynamicFieldDefinition
    ]:

        if not self._fields_schema:
            return []

        return [
            DynamicFieldDefinition.model_validate(
                item
            )
            for item in self._fields_schema
        ]

    @fields.setter
    def fields(
        self,
        value: list[
            DynamicFieldDefinition
        ],
    ) -> None:

        self._fields_schema = [
            field.model_dump(
                mode="json",
            )
            for field in value
        ]
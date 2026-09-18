from typing import Any

from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Table,
)

from sqlalchemy.dialects.postgresql import (
    JSONB,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from Core.Domain.Models.Base.base_models import (
    Base,
)

from Core.Domain.Models.Categories.category import (
    Category,
)

from Core.Domain.ViewModels.ValueObjects.Products.product_attribute_value import (
    ProductAttributeValue,
)


# =========================================================
# Product <-> Category
# Many To Many
# =========================================================

product_categories = Table(
    "product_categories",
    Base.metadata,

    Column(
        "product_id",
        ForeignKey(
            "products.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),

    Column(
        "category_id",
        ForeignKey(
            f"{Category.__tablename__}.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),
)


class Product(
    Base,
):

    # =========================================================
    # Basic
    # =========================================================

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # =========================================================
    # Categories
    # =========================================================

    categories: Mapped[
        list[Category]
    ] = relationship(
        secondary=product_categories,
        lazy="selectin",
        passive_deletes=True,
    )

    # =========================================================
    # Dynamic Attributes
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
        ProductAttributeValue
    ]:

        if not self._attributes:
            return []

        return [
            ProductAttributeValue.model_validate(
                item
            )
            for item in self._attributes
        ]

    @attributes.setter
    def attributes(
        self,
        value: list[
            ProductAttributeValue
        ],
    ) -> None:

        self._attributes = [
            item.model_dump(
                mode="json",
            )
            for item in value
        ]
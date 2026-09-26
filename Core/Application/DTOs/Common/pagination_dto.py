import math
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


TFilter = TypeVar("TFilter")
TItem = TypeVar("TItem")


class PagedRequestDto(BaseModel, Generic[TFilter]):
    """Generic Input DTO for pagination, sorting and optional filtering."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    page_number: int = Field(
        default=1,
        ge=1,
        description="شماره صفحه",
    )
    page_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="تعداد آیتم‌ها در هر صفحه",
    )
    sort_by: str | None = Field(
        default=None,
        description="نام ستون جهت مرتب‌سازی",
    )
    is_ascending: bool = Field(
        default=True,
        description="مرتب‌سازی صعودی (True) یا نزولی (False)",
    )
    filter: TFilter | None = Field(
        default=None,
        description="شیء فیلتر اختیاری",
    )


class PagedResultDto(BaseModel, Generic[TItem]):
    """Generic Output DTO for paginated responses."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    items: list[TItem] = Field(
        default_factory=list,
        description="لیست آیتم‌های صفحه جاری",
    )
    total_count: int = Field(
        description="تعداد کل آیتم‌ها",
    )
    page_number: int = Field(
        description="شماره صفحه جاری",
    )
    page_size: int = Field(
        description="تعداد آیتم‌ها در هر صفحه",
    )
    total_pages: int = Field(
        description="تعداد کل صفحات",
    )
    has_previous_page: bool = Field(
        default=False,
        description="آیا صفحه قبلی وجود دارد؟",
    )
    has_next_page: bool = Field(
        default=False,
        description="آیا صفحه بعدی وجود دارد؟",
    )

    @classmethod
    def create(
        cls,
        items: list[TItem],
        total_count: int,
        page_number: int,
        page_size: int,
    ) -> "PagedResultDto[TItem]":
        total_pages = math.ceil(total_count / page_size) if page_size > 0 else 0
        return cls(
            items=items,
            total_count=total_count,
            page_number=page_number,
            page_size=page_size,
            total_pages=total_pages,
            has_previous_page=page_number > 1,
            has_next_page=page_number < total_pages,
        )

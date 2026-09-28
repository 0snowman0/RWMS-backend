import math
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, model_validator


TFilter = TypeVar("TFilter")
TItem = TypeVar("TItem")


class PagedRequestDto(BaseModel, Generic[TFilter]):
    """Generic Input DTO for pagination, sorting and optional filtering."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    page_number: int = Field(
        default=1,
        description="شماره صفحه (یا -1 برای دریافت تمام داده‌ها)",
    )
    page_size: int = Field(
        default=10,
        description="تعداد آیتم‌ها در هر صفحه (یا -1 برای دریافت تمام داده‌ها)",
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

    @property
    def is_all_requested(self) -> bool:
        return self.page_number == -1 and self.page_size == -1

    @model_validator(mode="after")
    def validate_pagination(self) -> "PagedRequestDto[TFilter]":
        if self.page_number == -1 and self.page_size == -1:
            return self

        if self.page_number < 1:
            raise ValueError(
                "page_number must be greater than or equal to 1, or -1 when page_size is -1."
            )

        if self.page_size < 1 or self.page_size > 100:
            raise ValueError(
                "page_size must be between 1 and 100, or -1 when page_number is -1."
            )

        return self


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
        if page_number == -1 and page_size == -1:
            return cls(
                items=items,
                total_count=total_count,
                page_number=-1,
                page_size=-1,
                total_pages=1 if total_count > 0 else 0,
                has_previous_page=False,
                has_next_page=False,
            )

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

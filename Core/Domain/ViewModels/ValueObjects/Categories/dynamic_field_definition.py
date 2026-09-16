from decimal import Decimal
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

from Core.Domain.Enums.Categories.dynamic_field_type import (
    DynamicFieldType,
)
from Core.Domain.ViewModels.ValueObjects.Categories.dynamic_field_option import DynamicFieldOption




class DynamicFieldDefinition(
    BaseModel,
):

    model_config = ConfigDict(
        validate_assignment=True,
    )

    # =========================================================
    # Basic
    # =========================================================

    name: str
    # نام داخلی فیلد برای استفاده در کد و ذخیره مقدار
    # مثال:
    # weight
    # serial_number
    # camera_type

    title: str
    # عنوان نمایشی فیلد برای کاربر
    # مثال:
    # وزن
    # شماره سریال
    # نوع دوربین

    field_type: DynamicFieldType
    # نوع داده فیلد
    # مثال:
    # STRING
    # INTEGER
    # DECIMAL
    # BOOLEAN
    # DATE
    # SELECT
    # MULTI_SELECT

    # =========================================================
    # Behavior
    # =========================================================

    required: bool = False
    # مشخص می‌کند وارد کردن مقدار این فیلد اجباری است یا خیر

    unique: bool = False
    # مشخص می‌کند مقدار این فیلد باید یکتا باشد یا خیر
    # نحوه بررسی Unique بعداً در Business Logic کنترل می‌شود

    default_value: Any | None = None
    # مقدار پیش‌فرض فیلد در صورتی که کاربر مقداری وارد نکند

    auto_generate: bool = False
    # مشخص می‌کند مقدار فیلد باید به صورت خودکار توسط سیستم تولید شود
    # مثال:
    # کد کالا
    # شماره داخلی

    readonly: bool = False
    # اگر True باشد کاربر اجازه تغییر دستی مقدار را ندارد

    is_active: bool = True
    # مشخص می‌کند این فیلد فعال است یا خیر
    # فیلد غیرفعال بدون حذف شدن از ساختار نگهداری می‌شود

    # =========================================================
    # Display
    # =========================================================

    sort_order: int = 0
    # ترتیب نمایش فیلد نسبت به سایر فیلدها
    # عدد کمتر یعنی نمایش زودتر

    unit: str | None = None
    # واحد اندازه‌گیری فیلد
    # مثال:
    # kg
    # cm
    # V
    # W

    placeholder: str | None = None
    # متن راهنمای داخل Input
    # مثال:
    # وزن کالا را وارد کنید

    description: str | None = None
    # توضیح یا راهنمای کامل‌تر درباره فیلد

    show_in_list: bool = False
    # مشخص می‌کند این فیلد در لیست اصلی کالاها نمایش داده شود یا خیر

    # =========================================================
    # Numeric Rules
    # =========================================================

    min_value: Decimal | None = None
    # حداقل مقدار مجاز برای فیلدهای عددی

    max_value: Decimal | None = None
    # حداکثر مقدار مجاز برای فیلدهای عددی

    decimal_places: int | None = None
    # تعداد رقم اعشار مجاز
    # مثال:
    # 2 یعنی 12.50

    # =========================================================
    # String Rules
    # =========================================================

    min_length: int | None = None
    # حداقل تعداد کاراکتر مجاز برای فیلد متنی

    max_length: int | None = None
    # حداکثر تعداد کاراکتر مجاز برای فیلد متنی

    regex: str | None = None
    # الگوی اعتبارسنجی متن
    # برای کنترل فرمت‌های خاص
    # مثال:
    # کد کالا
    # شماره سریال
    # فرمت اختصاصی

    # =========================================================
    # Select / Multi Select
    # =========================================================

    options: list[
        DynamicFieldOption
    ] = Field(
        default_factory=list
    )
    # گزینه‌های قابل انتخاب برای:
    # SELECT
    # MULTI_SELECT
    #
    # برای سایر Field Typeها معمولاً خالی است

    # =========================================================
    # Future Settings
    # =========================================================

    settings: dict[
        str,
        Any,
    ] = Field(
        default_factory=dict
    )
    # تنظیمات آزاد و توسعه‌پذیر برای قابلیت‌های آینده
    # تا برای هر قابلیت جدید مجبور به تغییر ساختار اصلی مدل نباشیم
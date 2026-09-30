from datetime import date, datetime, timezone
from typing import Any
import zoneinfo

from dateutil.parser import isoparse
from fastapi.encoders import jsonable_encoder
import jdatetime

from Core.Application.Commons.base_response import BaseResponse

TEHRAN_TZ = zoneinfo.ZoneInfo("Asia/Tehran")


def to_jalali_datetime(dt: datetime | None) -> str | None:
    """
    تبدیل شیء datetime به رشته شمسی با ارقام انگلیسی.
    فرمت: YYYY/MM/DD HH:MM:SS
    زمان‌های دارای منطقه زمانی به افق تهران منتقل می‌شوند.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc).astimezone(TEHRAN_TZ)
    else:
        dt = dt.astimezone(TEHRAN_TZ)
    jdt = jdatetime.datetime.fromgregorian(datetime=dt)
    return jdt.strftime("%Y/%m/%d %H:%M:%S")


def to_jalali_date(d: date | None) -> str | None:
    """
    تبدیل شیء date به رشته شمسی با ارقام انگلیسی.
    فرمت: YYYY/MM/DD
    """
    if d is None:
        return None
    jdt = jdatetime.date.fromgregorian(date=d)
    return jdt.strftime("%Y/%m/%d")


def is_date_key(key: str) -> bool:
    """
    تشخیص اینکه آیا نام فیلد مربوط به تاریخ یا زمان است.
    """
    k = key.lower()
    return (
        k.endswith("_at")
        or k.endswith("_date")
        or k == "date"
        or k.startswith("date_")
    )


def try_convert_iso_str_to_jalali(val: str) -> str:
    """
    تلاش برای تبدیل رشته‌های تاریخ میلادی ISO به شمسی.
    در صورت عدم تطابق، رشته اصلی بازگردانده می‌شود.
    """
    if not isinstance(val, str) or len(val) < 10:
        return val
    try:
        parsed = isoparse(val)
        if isinstance(parsed, datetime):
            if len(val) == 10 and "T" not in val and " " not in val:
                return to_jalali_date(parsed.date())
            return to_jalali_datetime(parsed)
        elif isinstance(parsed, date):
            return to_jalali_date(parsed)
    except Exception:
        pass
    return val


def convert_datetimes_to_jalali(obj: Any, current_key: str | None = None) -> Any:
    """
    پیمایش بازگشتی ساختار داده و تبدیل تاریخ‌ها و رشته‌های تاریخ‌محور به شمسی.
    """
    if isinstance(obj, dict):
        return {
            k: convert_datetimes_to_jalali(v, current_key=str(k))
            for k, v in obj.items()
        }
    elif isinstance(obj, list):
        return [convert_datetimes_to_jalali(item, current_key=current_key) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_datetimes_to_jalali(item, current_key=current_key) for item in obj)
    elif isinstance(obj, str) and current_key and is_date_key(current_key):
        return try_convert_iso_str_to_jalali(obj)
    return obj


def format_response_content(result: BaseResponse[Any]) -> Any:
    """
    سریالایز و تبدیل کامل داده‌های BaseResponse به دیکشنری JSON-Ready با تاریخ‌های شمسی.
    """
    raw_content = result.model_dump(mode="python")
    encoded = jsonable_encoder(
        raw_content,
        custom_encoder={
            datetime: to_jalali_datetime,
            date: to_jalali_date,
        },
    )
    return convert_datetimes_to_jalali(encoded)

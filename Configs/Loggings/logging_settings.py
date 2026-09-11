from dataclasses import dataclass

from Core.Domain.Enums.Loggings.log_level import (
    LogLevel,
)


@dataclass(
    frozen=True,
    slots=True,
)
class LoggingSettings:

    # کل سیستم Logging روشن / خاموش
    enabled: bool = True

    # حداقل Level قابل ثبت
    minimum_level: LogLevel = LogLevel.INFO

    # ذخیره در PostgreSQL
    database_enabled: bool = True

    # نمایش همزمان در Console
    console_enabled: bool = False

    # تعداد Log برای Flush گروهی
    batch_size: int = 50

    # Flush زمانی
    # اگر None باشد، Flush زمانی غیرفعال است
    flush_interval_seconds: float | None = 5.0

    # حداکثر تعداد Log داخل Queue
    max_queue_size: int = 10_000

    # اطلاعات Request
    include_request_context: bool = True

    # اطلاعات User
    # فعلاً UserId نداریم ولی ساختارش آماده است
    include_user_context: bool = True

    # StackTrace خطاها ذخیره شود؟
    include_stack_trace: bool = True

    # اگر ذخیره Log در PostgreSQL شکست خورد
    # Logها در فایل ذخیره شوند
    fallback_to_file: bool = True

    # مسیر فایل پشتیبان
    fallback_file_path: str = (
        "logs/logging-fallback.log"
    )

    def __post_init__(
        self,
    ) -> None:

        if self.batch_size <= 0:
            raise ValueError(
                "batch_size must be greater than 0."
            )

        if (
            self.flush_interval_seconds is not None
            and self.flush_interval_seconds <= 0
        ):
            raise ValueError(
                "flush_interval_seconds must be "
                "greater than 0 or None."
            )

        if self.max_queue_size <= 0:
            raise ValueError(
                "max_queue_size must be greater than 0."
            )

        if (
            self.fallback_to_file
            and not self.fallback_file_path.strip()
        ):
            raise ValueError(
                "fallback_file_path cannot be empty."
            )
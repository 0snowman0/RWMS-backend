from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class ExceptionHandlerSettings:

    # فعال / غیرفعال بودن Global Exception Handler
    enabled: bool = True

    # Exceptionهای کنترل‌نشده Log شوند؟
    log_exceptions: bool = True

    # متن واقعی Exception به Client نمایش داده شود؟
    # برای Production بهتر است False باشد
    include_exception_message_in_response: bool = True

    # پیام پیش‌فرض برای خطاهای کنترل‌نشده
    default_message: str = (
        "An unexpected error occurred."
    )

    # متن پیش‌فرض داخل errors
    default_error_message: str = (
        "Internal server error."
    )

    # HTTP Status Code پیش‌فرض
    default_status_code: int = 500

    def __post_init__(
        self,
    ) -> None:

        if not self.default_message.strip():
            raise ValueError(
                "default_message cannot be empty."
            )

        if not self.default_error_message.strip():
            raise ValueError(
                "default_error_message cannot be empty."
            )

        if not (
            400
            <= self.default_status_code
            <= 599
        ):
            raise ValueError(
                "default_status_code must be "
                "between 400 and 599."
            )
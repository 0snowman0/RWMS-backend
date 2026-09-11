from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from Configs.ExceptionHandlers.exception_handler_settings import (
    ExceptionHandlerSettings,
)

from Core.Application.Commons.base_response import (
    BaseResponse,
)

from Core.Application.Loggings.logging_context import (
    LoggingContextAccessor,
)


class GlobalExceptionHandler:

    def __init__(
        self,
        settings: ExceptionHandlerSettings,
    ) -> None:

        self._settings = settings

    async def handle(
        self,
        request: Request,
        exception: Exception,
    ) -> JSONResponse:

        # =====================================================
        # HTTP Status in Logging Context
        # =====================================================

        context = LoggingContextAccessor.get()

        if context is not None:
            context.status_code = (
                self._settings.default_status_code
            )

        # =====================================================
        # Logging
        # =====================================================

        if self._settings.log_exceptions:

            try:

                logger = (
                    request.app.state.application_logger
                )

                logger.exception(
                    message=(
                        "Unhandled application exception."
                    ),
                    exception=exception,
                    properties={
                        "exception_type": type(
                            exception
                        ).__name__,
                        "http_method": request.method,
                        "path": request.url.path,
                    },
                )

            except Exception:
                # Exception Handler خودش نباید
                # به خاطر مشکل Logging خراب شود
                pass

        # =====================================================
        # Error Message
        # =====================================================

        if (
            self._settings
            .include_exception_message_in_response
        ):

            errors = [
                str(exception)
            ]

        else:

            errors = [
                self._settings.default_error_message
            ]

        # =====================================================
        # Base Response
        # =====================================================

        result = (
            BaseResponse.internal_server_error(
                message=(
                    self._settings.default_message
                ),
                errors=errors,
            )
        )

        # =====================================================
        # HTTP Response
        # =====================================================

        return JSONResponse(
            status_code=(
                self._settings.default_status_code
            ),
            content=jsonable_encoder(
                result.model_dump(
                    mode="python"
                )
            ),
        )
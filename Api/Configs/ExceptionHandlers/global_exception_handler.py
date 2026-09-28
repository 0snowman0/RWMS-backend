from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

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
        # Validation Errors (HTTP 422)
        # =====================================================

        context = LoggingContextAccessor.get()

        if isinstance(exception, (RequestValidationError, ValidationError)):
            if context is not None:
                context.status_code = (
                    status.HTTP_422_UNPROCESSABLE_ENTITY
                )

            error_messages: list[str] = []
            if hasattr(exception, "errors"):
                for err in exception.errors():
                    msg = err.get("msg") if isinstance(err, dict) else str(err)
                    loc = " -> ".join(str(l) for l in err.get("loc", [])) if isinstance(err, dict) else ""
                    error_messages.append(f"{loc}: {msg}" if loc else str(msg))
            else:
                error_messages.append(str(exception))

            val_result = BaseResponse.validation_error(
                message="Validation error.",
                errors=error_messages,
            )

            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=jsonable_encoder(
                    val_result.model_dump(
                        mode="python"
                    )
                ),
            )

        # =====================================================
        # HTTP Status in Logging Context
        # =====================================================

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
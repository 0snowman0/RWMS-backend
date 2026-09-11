from fastapi import FastAPI

from Api.Configs.ExceptionHandlers.global_exception_handler import GlobalExceptionHandler
from Configs.ExceptionHandlers.exception_handler_settings import (
    ExceptionHandlerSettings,
)


def configure_exception_handlers(
    app: FastAPI,
) -> None:

    settings = ExceptionHandlerSettings()

    handler = GlobalExceptionHandler(
        settings=settings,
    )

    if not settings.enabled:
        return

    app.add_exception_handler(
        Exception,
        handler.handle,
    )

    app.state.exception_handler_settings = (
        settings
    )

    app.state.global_exception_handler = (
        handler
    )
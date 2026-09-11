from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import (
    BaseHTTPMiddleware,
)

from Core.Application.Loggings.logging_context import (
    LoggingContext,
    LoggingContextAccessor,
)


class LoggingContextMiddleware(
    BaseHTTPMiddleware,
):

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):

        request_id = str(
            uuid4()
        )

        correlation_id = (
            request.headers.get(
                "X-Correlation-ID"
            )
            or request_id
        )

        client_ip = None

        if request.client is not None:
            client_ip = request.client.host

        context = LoggingContext(
            request_id=request_id,
            correlation_id=correlation_id,
            ip_address=client_ip,
            user_id=None,
            http_method=request.method,
            path=request.url.path,
            status_code=None,
        )

        token = (
            LoggingContextAccessor.set(
                context
            )
        )

        try:

            response = await call_next(
                request
            )

            context.status_code = (
                response.status_code
            )

            response.headers[
                "X-Request-ID"
            ] = request_id

            response.headers[
                "X-Correlation-ID"
            ] = correlation_id

            return response

        finally:

            LoggingContextAccessor.reset(
                token
            )
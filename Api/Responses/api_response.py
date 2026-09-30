from typing import Any

from fastapi import status
from fastapi.responses import JSONResponse


from Core.Application.Commons.base_response import BaseResponse
from Core.Application.Commons.date_converter import (
    format_response_content,
)
from Core.Domain.Enums.Responses.response_status import (
    ResponseStatus,
)


def to_api_response(
    result: BaseResponse[Any],
) -> JSONResponse:

    status_codes: dict[
        ResponseStatus,
        int,
    ] = {

        ResponseStatus.SUCCESS:
            status.HTTP_200_OK,

        ResponseStatus.CREATED:
            status.HTTP_201_CREATED,

        ResponseStatus.FAILED:
            status.HTTP_400_BAD_REQUEST,

        ResponseStatus.UNAUTHORIZED:
            status.HTTP_401_UNAUTHORIZED,

        ResponseStatus.FORBIDDEN:
            status.HTTP_403_FORBIDDEN,

        ResponseStatus.NOT_FOUND:
            status.HTTP_404_NOT_FOUND,

        ResponseStatus.CONFLICT:
            status.HTTP_409_CONFLICT,

        ResponseStatus.VALIDATION_ERROR:
            status.HTTP_422_UNPROCESSABLE_ENTITY,
    }

    status_code = status_codes.get(
        result.status,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )

    return JSONResponse(
        status_code=status_code,
        content=format_response_content(result),
    )
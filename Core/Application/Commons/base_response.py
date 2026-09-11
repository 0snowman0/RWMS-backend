from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from Core.Domain.Enums.Responses.response_status import (
    ResponseStatus,
)


T = TypeVar("T")


class BaseResponse(
    BaseModel,
    Generic[T],
):
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
    is_success: bool

    message: str | None = None

    errors: list[str] = Field(
        default_factory=list
    )

    data: T | None = None

    status: ResponseStatus

    # ---------------------------------------------------------
    # Success
    # ---------------------------------------------------------

    @classmethod
    def success(
        cls,
        data: T | None = None,
        message: str | None = None,
    ) -> "BaseResponse[T]":

        return cls(
            is_success=True,
            message=message,
            errors=[],
            data=data,
            status=ResponseStatus.SUCCESS,
        )

    # ---------------------------------------------------------
    # Failed
    # ---------------------------------------------------------

    @classmethod
    def fail(
        cls,
        message: str | None = None,
        errors: list[str] | None = None,
        data: T | None = None,
    ) -> "BaseResponse[T]":

        return cls(
            is_success=False,
            message=message,
            errors=errors or [],
            data=data,
            status=ResponseStatus.FAILED,
        )

    # ---------------------------------------------------------
    # Not Found
    # ---------------------------------------------------------

    @classmethod
    def not_found(
        cls,
        message: str | None = None,
        errors: list[str] | None = None,
    ) -> "BaseResponse[T]":

        return cls(
            is_success=False,
            message=message,
            errors=errors or [],
            data=None,
            status=ResponseStatus.NOT_FOUND,
        )

    # ---------------------------------------------------------
    # Forbidden
    # ---------------------------------------------------------

    @classmethod
    def forbidden(
        cls,
        message: str | None = None,
        errors: list[str] | None = None,
    ) -> "BaseResponse[T]":

        return cls(
            is_success=False,
            message=message,
            errors=errors or [],
            data=None,
            status=ResponseStatus.FORBIDDEN,
        )

    # ---------------------------------------------------------
    # Unauthorized
    # ---------------------------------------------------------

    @classmethod
    def unauthorized(
        cls,
        message: str | None = None,
        errors: list[str] | None = None,
    ) -> "BaseResponse[T]":

        return cls(
            is_success=False,
            message=message,
            errors=errors or [],
            data=None,
            status=ResponseStatus.UNAUTHORIZED,
        )

    # ---------------------------------------------------------
    # Validation Error
    # ---------------------------------------------------------

    @classmethod
    def validation_error(
        cls,
        message: str | None = None,
        errors: list[str] | None = None,
    ) -> "BaseResponse[T]":

        return cls(
            is_success=False,
            message=message,
            errors=errors or [],
            data=None,
            status=ResponseStatus.VALIDATION_ERROR,
        )

    # ---------------------------------------------------------
    # Conflict
    # ---------------------------------------------------------

    @classmethod
    def conflict(
        cls,
        message: str | None = None,
        errors: list[str] | None = None,
    ) -> "BaseResponse[T]":

        return cls(
            is_success=False,
            message=message,
            errors=errors or [],
            data=None,
            status=ResponseStatus.CONFLICT,
        )
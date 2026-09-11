from enum import Enum


class ResponseStatus(
    str,
    Enum,
):
    SUCCESS = "success"
    FAILED = "failed"
    NOT_FOUND = "not_found"
    FORBIDDEN = "forbidden"
    UNAUTHORIZED = "unauthorized"
    VALIDATION_ERROR = "validation_error"
    CONFLICT = "conflict"
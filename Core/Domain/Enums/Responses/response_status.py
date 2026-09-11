from enum import Enum


class ResponseStatus(
    str,
    Enum,
):
    SUCCESS = "success"
    CREATED = "created"
    FAILED = "failed"
    NOT_FOUND = "not_found"
    FORBIDDEN = "forbidden"
    UNAUTHORIZED = "unauthorized"
    VALIDATION_ERROR = "validation_error"
    CONFLICT = "conflict"
    INTERNAL_SERVER_ERROR = "internal_server_error"
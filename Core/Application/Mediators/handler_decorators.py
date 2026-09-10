from typing import TypeVar


T = TypeVar("T")


HANDLER_REQUEST_ATTRIBUTE = "__mediator_request__"


def handler_for(
    request_type: type,
):
    def decorator(
        handler_type: T,
    ) -> T:

        setattr(
            handler_type,
            HANDLER_REQUEST_ATTRIBUTE,
            request_type,
        )

        return handler_type

    return decorator
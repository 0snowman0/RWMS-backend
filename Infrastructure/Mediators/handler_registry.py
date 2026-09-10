
from Core.Application.Contracts.Mediators.handler_registry import IHandlerRegistry
from Core.Application.Contracts.Mediators.mediator import IRequestHandler


class HandlerRegistry(IHandlerRegistry):

    def __init__(self):
        self._handlers: dict[
            type,
            type[IRequestHandler],
        ] = {}

    def register(
        self,
        request_type: type,
        handler_type: type[IRequestHandler],
    ) -> None:

        if request_type in self._handlers:
            raise ValueError(
                f"Handler for "
                f"'{request_type.__name__}' "
                f"is already registered."
            )

        self._handlers[
            request_type
        ] = handler_type

    def get_handler_type(
        self,
        request_type: type,
    ) -> type[IRequestHandler]:

        handler_type = self._handlers.get(
            request_type
        )

        if handler_type is None:
            raise KeyError(
                f"Handler for "
                f"'{request_type.__name__}' "
                f"was not found."
            )

        return handler_type
from Core.Application.Contracts.Loggings.logger import (
    ILogger,
)

from Core.Application.Contracts.Mediators.mediator import (
    IPipelineBehavior,
    NextHandler,
)

from Core.Application.Mediators.behavior_decorators import (
    behavior,
)

from Core.Domain.Enums.Mediators.mediator import (
    BehaviorType,
)


@behavior(BehaviorType.LOGGING)
class LoggingBehavior(
    IPipelineBehavior,
):

    def __init__(
        self,
        logger: ILogger,
    ) -> None:

        self._logger = logger

    async def handle(
        self,
        request,
        next_handler: NextHandler,
    ):

        request_name = type(
            request
        ).__name__

        # ==============================================
        # Request
        # ==============================================

        self._logger.info(
            f"Mediator Request: {request_name}",
            properties={
                "request_type": request_name,
                "request": repr(request),
            },
        )

        result = await next_handler()

        # ==============================================
        # Response
        # ==============================================

        self._logger.info(
            f"Mediator Response: {request_name}",
            properties={
                "request_type": request_name,
                "response": repr(result),
            },
        )

        return result
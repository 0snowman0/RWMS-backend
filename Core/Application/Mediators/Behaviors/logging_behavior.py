from Core.Application.Contracts.Mediators.mediator import IPipelineBehavior, NextHandler
from Core.Application.Mediators.behavior_decorators import behavior
from Core.Domain.Enums.Mediators.mediator import BehaviorType


@behavior(BehaviorType.LOGGING)
class LoggingBehavior(
    IPipelineBehavior,
):

    async def handle(
        self,
        request,
        next_handler: NextHandler,
    ):
        print(
            f"[Mediator Request] "
            f"{type(request).__name__}: "
            f"{request}"
        )

        result = await next_handler()

        print(
            f"[Mediator Response] "
            f"{type(request).__name__}: "
            f"{result}"
        )

        return result
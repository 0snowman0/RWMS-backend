from Core.Application.Contracts.Mediators.mediator import IPipelineBehavior, NextHandler
from Core.Application.Mediators.behavior_decorators import behavior
from Core.Domain.Enums.Mediators.mediator import BehaviorType


@behavior(BehaviorType.VALIDATION)
class ValidationBehavior(
    IPipelineBehavior,
):

    async def handle(
        self,
        request,
        next_handler: NextHandler,
    ):
        print("ValidationBehavior 1")
        return await next_handler()
    
from Core.Application.Contracts.DataBases.UnitOfWorks.unit_of_works import (
    IUnitOfWork,
)
from Core.Application.Contracts.Mediators.mediator import IPipelineBehavior, NextHandler
from Core.Application.Mediators.behavior_decorators import behavior
from Core.Domain.Enums.Mediators.mediator import BehaviorType



@behavior(BehaviorType.TRANSACTION)
class TransactionBehavior(
    IPipelineBehavior,
):

    def __init__(
        self,
        uow: IUnitOfWork,
    ):
        self._uow = uow

    async def handle(
        self,
        request,
        next_handler: NextHandler,
    ):
        async with self._uow:

            result = await next_handler()

            await self._uow.save_changes()

            return result

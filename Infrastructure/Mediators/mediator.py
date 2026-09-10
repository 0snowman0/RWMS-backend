
from Core.Application.Contracts.Mediators.behavior_factory import IBehaviorFactory
from Core.Application.Contracts.Mediators.behavior_registry import IBehaviorRegistry
from Core.Application.Contracts.Mediators.handler_factory import IHandlerFactory
from Core.Application.Contracts.Mediators.handler_registry import IHandlerRegistry
from Core.Application.Contracts.Mediators.mediator import IMediator
from Core.Application.Mediators.behavior_policy_resolver import BehaviorPolicyResolver


class Mediator(IMediator):

    def __init__(
        self,
        handler_registry: IHandlerRegistry,
        handler_factory: IHandlerFactory,
        behavior_registry: IBehaviorRegistry,
        behavior_factory: IBehaviorFactory,
        behavior_policy_resolver: BehaviorPolicyResolver,
    ):
        self._handler_registry = handler_registry
        self._handler_factory = handler_factory

        self._behavior_registry = behavior_registry
        self._behavior_factory = behavior_factory

        self._behavior_policy_resolver = (
            behavior_policy_resolver
        )

    async def send(
        self,
        request,
    ):
        # -------------------------
        # Handler
        # -------------------------

        request_type = type(
            request
        )

        handler_type = (
            self._handler_registry
            .get_handler_type(
                request_type
            )
        )

        handler = (
            self._handler_factory.create(
                handler_type
            )
        )

        # -------------------------
        # Behavior Policy
        # -------------------------

        behavior_types = (
            self._behavior_policy_resolver
            .resolve(
                request
            )
        )

        # -------------------------
        # Handler آخر Pipeline
        # -------------------------

        async def execute_handler():
            return await handler.handle(
                request
            )

        next_handler = execute_handler

        # -------------------------
        # ساخت Pipeline
        # -------------------------

        for behavior_type in reversed(
            behavior_types
        ):

            behavior_class = (
                self._behavior_registry
                .get_behavior_class(
                    behavior_type
                )
            )

            behavior = (
                self._behavior_factory.create(
                    behavior_class
                )
            )

            current_next = next_handler

            async def execute_behavior(
                behavior=behavior,
                current_next=current_next,
            ):
                return await behavior.handle(
                    request,
                    current_next,
                )

            next_handler = execute_behavior

        # -------------------------
        # Execute Pipeline
        # -------------------------

        return await next_handler()
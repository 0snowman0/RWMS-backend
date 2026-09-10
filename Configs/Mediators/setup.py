from fastapi import FastAPI

from Infrastructure.Mediators.behavior_loader import BehaviorLoader
from Infrastructure.Mediators.behavior_registry import BehaviorRegistry
from Infrastructure.Mediators.handler_loader import HandlerLoader
from Infrastructure.Mediators.handler_registry import HandlerRegistry

def configure_mediator(
    app: FastAPI,
) -> None:

    handler_registry = HandlerRegistry()

    behavior_registry = BehaviorRegistry()

    handler_loader = HandlerLoader(
        registry=handler_registry,
    )

    behavior_loader = BehaviorLoader(
        registry=behavior_registry,
    )

    behavior_loader.load(
        "Core.Application.Mediators.Behaviors"
    )

    handler_loader.load(
        "Core.Application.Features"
    )

    app.state.mediator_handler_registry = (
        handler_registry
    )

    app.state.mediator_behavior_registry = (
        behavior_registry
    )

    app.state.mediator_handler_loader = (
        handler_loader
    )
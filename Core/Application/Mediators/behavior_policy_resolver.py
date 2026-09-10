from Configs.Mediators.behavior_policy import MEDIATOR_BEHAVIOR_POLICIES
from Core.Application.Mediators.decorators import REQUEST_TYPE_ATTRIBUTE, REQUIRE_BEHAVIORS_ATTRIBUTE, SKIP_BEHAVIORS_ATTRIBUTE
from Core.Domain.Enums.Mediators.mediator import BehaviorType


class BehaviorPolicyResolver:

    def resolve(
        self,
        request: object,
    ) -> tuple[BehaviorType, ...]:

        request_class = type(request)

        request_type = getattr(
            request_class,
            REQUEST_TYPE_ATTRIBUTE,
            None,
        )

        if request_type is None:
            raise ValueError(
                f"Request type is not defined for "
                f"{request_class.__name__}"
            )

        default_behaviors = list(
            MEDIATOR_BEHAVIOR_POLICIES.get(
                request_type,
                (),
            )
        )

        skipped_behaviors = set(
            getattr(
                request_class,
                SKIP_BEHAVIORS_ATTRIBUTE,
                (),
            )
        )

        required_behaviors = set(
            getattr(
                request_class,
                REQUIRE_BEHAVIORS_ATTRIBUTE,
                (),
            )
        )

        conflict = (
            skipped_behaviors
            & required_behaviors
        )

        if conflict:
            raise ValueError(
                f"Behaviors cannot be both skipped "
                f"and required: {conflict}"
            )

        final_behaviors = [
            behavior
            for behavior in default_behaviors
            if behavior not in skipped_behaviors
        ]

        for behavior in required_behaviors:

            if behavior not in final_behaviors:
                final_behaviors.append(
                    behavior
                )

        return tuple(
            final_behaviors
        )
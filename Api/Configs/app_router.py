from fastapi import APIRouter

from Api.RateLimiting.rate_limit_route import RateLimitedRoute


class AppRouter(APIRouter):

    def __init__(
        self,
        *args,
        **kwargs,
    ):

        kwargs.setdefault(
            "route_class",
            RateLimitedRoute,
        )

        if "tags" not in kwargs or kwargs["tags"] is None:

            prefix = kwargs.get(
                "prefix",
                "",
            )

            tag = (
                prefix
                .strip("/")
                .replace("-", " ")
                .replace("_", " ")
                .title()
            )

            if tag:
                kwargs["tags"] = [tag]

        super().__init__(
            *args,
            **kwargs,
        )
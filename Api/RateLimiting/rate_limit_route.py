from collections.abc import Callable

from fastapi import HTTPException, Request, Response
from fastapi.routing import APIRoute

from Api.RateLimiting.policy_resolver import RateLimitPolicyResolver



class RateLimitedRoute(APIRoute):

    def get_route_handler(
        self,
    ) -> Callable:

        original_route_handler = (
            super().get_route_handler()
        )

        endpoint = self.endpoint

        async def custom_route_handler(
            request: Request,
        ) -> Response:

            policy_provider = (
                request.app.state
                .rate_limit_policy_provider
            )


            policy_resolver = (
                RateLimitPolicyResolver(
                    policy_provider
                )
            )

            policy = policy_resolver.resolve(
                endpoint
            )


            limiter_resolver = (
                request.app.state
                .rate_limiter_resolver
            )

            limiter = limiter_resolver.resolve(
                policy
            )
            
            client_ip = (
                request.client.host
                if request.client
                else "unknown"
            )

            key = f"ip:{client_ip}"


            result = await limiter.acquire(
                key=key,
                policy=policy,
            )

            if not result.is_allowed:

                headers = {
                    "X-RateLimit-Limit":
                        str(result.limit),

                    "X-RateLimit-Remaining":
                        str(result.remaining),
                }

                if (
                    result.retry_after_seconds
                    is not None
                ):
                    headers["Retry-After"] = str(
                        result.retry_after_seconds
                    )

                raise HTTPException(
                    status_code=429,
                    detail="Too many requests.",
                    headers=headers,
                )


            response = await original_route_handler(
                request
            )

            response.headers[
                "X-RateLimit-Limit"
            ] = str(result.limit)

            response.headers[
                "X-RateLimit-Remaining"
            ] = str(result.remaining)

            return response

        return custom_route_handler
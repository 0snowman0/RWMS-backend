from Core.Application.Commons.base_response import BaseResponse
from Core.Application.Contracts.DataBases.UnitOfWorks.unit_of_works import (
    IUnitOfWork,
)

from Core.Application.Contracts.Loggings.logger import ILogger
from Core.Application.Contracts.Mapper.mapper import (
    IMapper,
)


from Core.Application.Contracts.Mediators.mediator import IRequestHandler
from Core.Application.Features.Users.Requests.Commands.create_user import (
    CreateUserCommand,
)

from Core.Application.Mediators.handler_decorators import handler_for
from Core.Domain.Models.user import (
    User,
)


@handler_for(CreateUserCommand)
class CreateUserCommandHandler(
    IRequestHandler[
        CreateUserCommand,
        BaseResponse[User],
    ]
):

    def __init__(
        self,
        uow: IUnitOfWork,
        mapper: IMapper,
        logger: ILogger,
    ):
        self._uow = uow
        self._mapper = mapper
        self._logger = logger

    async def handle(
        self,
        request: CreateUserCommand,
    ) -> BaseResponse[User]:

        self._logger.info(
            "CreateUserCommand started.",
            properties={
                "email": request.data.email,
            },
        )

        try:

            user = self._mapper.map(
                request.data,
                User,
            )

            self._logger.debug(
                "User DTO mapped to User entity.",
                properties={
                    "email": user.email,
                },
            )

            await self._uow.users.add(
                user
            )

            self._logger.info(
                "User added to repository.",
                properties={
                    "email": user.email,
                },
            )

            return BaseResponse[User].success(
                data=user,
                message="User created successfully.",
            )

        except Exception as ex:

            self._logger.exception(
                message="CreateUserCommand failed.",
                exception=ex,
                properties={
                    "email": request.data.email,
                },
            )

            raise
from Core.Application.Contracts.DataBases.UnitOfWorks.unit_of_works import (
    IUnitOfWork,
)

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
        User,
    ]
):

    def __init__(
        self,
        uow: IUnitOfWork,
        mapper: IMapper,
    ):
        self._uow = uow
        self._mapper = mapper

    async def handle(
        self,
        request: CreateUserCommand,
    ) -> User:

        user = self._mapper.map(
            request.data,
            User,
        )

        await self._uow.users.add(
            user
        )

        return user
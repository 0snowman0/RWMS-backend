from fastapi import HTTPException

from Api.Configs.app_router import AppRouter

from Configs.dependencies import (
    DatabaseRoutineExecutorDependency,
    UOWDependency,
)

from Core.Application.DTOs.DatabaseRoutines.routine_user_test import (
    RoutineUserDto,
)


router = AppRouter(
    tags=["SPs"],
)


# ============================================================
# execute()
# ============================================================

@router.post(
    "/execute/{user_id}"
)
async def test_execute(
    user_id: int,
    is_active: bool,
    routine: DatabaseRoutineExecutorDependency,
    uow: UOWDependency,
):

    await routine.execute(
        "public.sp_test_set_user_active",
        {
            "p_user_id": user_id,
            "p_is_active": is_active,
        },
    )

    await uow.save_changes()

    return {
        "message": "Procedure executed successfully",
        "user_id": user_id,
        "is_active": is_active,
    }


# ============================================================
# execute_scalar()
# ============================================================

@router.get(
    "/scalar"
)
async def test_scalar(
    routine: DatabaseRoutineExecutorDependency,
):

    result = await routine.execute_scalar(
        "public.fn_test_user_count",
    )

    return {
        "count": result,
    }


# ============================================================
# execute_raw()
# ============================================================

@router.get(
    "/raw"
)
async def test_raw(
    routine: DatabaseRoutineExecutorDependency,
):

    result = await routine.execute_raw(
        "public.fn_test_users_raw",
    )

    return {
        "result": result,
    }


# ============================================================
# execute_one()
# ============================================================

@router.get(
    "/one/{user_id}"
)
async def test_one(
    user_id: int,
    routine: DatabaseRoutineExecutorDependency,
):

    result = await routine.execute_one(
        "public.fn_test_user_by_id",
        RoutineUserDto,
        {
            "p_user_id": user_id,
        },
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return result


# ============================================================
# execute_list()
# ============================================================

@router.get(
    "/list"
)
async def test_list(
    routine: DatabaseRoutineExecutorDependency,
    is_active: bool | None = None,
):

    params = {}

    if is_active is not None:
        params[
            "p_is_active"
        ] = is_active

    result = await routine.execute_list(
        "public.fn_test_users_list",
        RoutineUserDto,
        params,
    )

    return result
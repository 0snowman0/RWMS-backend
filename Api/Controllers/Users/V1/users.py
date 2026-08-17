from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1/users",
     tags=["Users V1"],
)


@router.get("/")
def get_users():
    return {"message": "Get users - V1"}


@router.get("/{user_id}")
def get_user(user_id: int):
    return {
        "message": "Get user - V1",
        "user_id": user_id,
    }

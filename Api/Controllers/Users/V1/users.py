from fastapi import APIRouter

router = APIRouter(
    tags=["Users"]
)

@router.get("/users")
def get_users():
    return {"version": "v1", "message": "Users API"}


@router.get("/users/{user_id}")
def get_user(user_id: int):
    return {
        "version": "v1",
        "user_id": user_id,
    }
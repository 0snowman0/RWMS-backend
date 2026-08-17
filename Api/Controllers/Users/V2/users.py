from fastapi import APIRouter

router = APIRouter(
    tags=["Users"]
)


@router.get("/users")
def get_users():
    return {"version": "v2", "message": "Users API V2"}
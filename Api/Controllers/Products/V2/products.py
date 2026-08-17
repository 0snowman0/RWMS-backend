from fastapi import APIRouter


router = APIRouter(
    tags=["Products"]
)


@router.get("/products")
def get_products():
    return {"version": "v2", "message": "Products API V2"}
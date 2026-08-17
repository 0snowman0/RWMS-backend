from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1/products",
    tags=["Products V1"],
)


@router.get("/")
def get_products():
    return {"message": "Get products - V1"}


@router.get("/{product_id}")
def get_product(product_id: int):
    return {
        "message": "Get product - V1",
        "product_id": product_id,
    }
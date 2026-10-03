from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services.product_service import (
    create_product,
    get_product,
    get_products,
    update_product,
    delete_product,
)


router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=201,
)
def add_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
):
    return create_product(db, product_data)


@router.get(
    "/",
    response_model=list[ProductResponse],
)
def search_products(
    name: str | None = Query(default=None),
    category: str | None = Query(default=None),
    product_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return get_products(
        db,
        name=name,
        category=category,
        product_id=product_id,
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
def view_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = get_product(db, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
)
def update_product_details(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
):
    product = update_product(
        db,
        product_id,
        product_data,
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product


@router.delete(
    "/{product_id}",
    response_model=ProductResponse,
)
def remove_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = delete_product(db, product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product
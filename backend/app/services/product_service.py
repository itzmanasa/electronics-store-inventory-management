from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


def create_product(db: Session, product_data: ProductCreate) -> Product:
    product = Product(
        name=product_data.name,
        category=product_data.category,
        price=product_data.price,
        quantity=product_data.quantity,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


def get_product(db: Session, product_id: int) -> Product | None:
    return db.query(Product).filter(Product.id == product_id).first()


def get_products(
    db: Session,
    name: str | None = None,
    category: str | None = None,
    product_id: int | None = None,
) -> list[Product]:

    query = db.query(Product)

    if product_id is not None:
        query = query.filter(Product.id == product_id)

    if name:
        query = query.filter(Product.name.ilike(f"%{name}%"))

    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))

    return query.all()


def update_product(
    db: Session,
    product_id: int,
    product_data: ProductUpdate,
) -> Product | None:

    product = get_product(db, product_id)

    if product is None:
        return None

    update_data = product_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return product


def delete_product(db: Session, product_id: int) -> Product | None:
    product = get_product(db, product_id)

    if product is None:
        return None

    db.delete(product)
    db.commit()

    return product
from sqlalchemy import Column, Integer, String, Numeric

from app.database.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
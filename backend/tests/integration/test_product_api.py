from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.database import Base
from app.main import app
from app.routers.product import get_db


# Use a separate in-memory SQLite database for integration tests.
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def setup_database():
    Base.metadata.create_all(bind=engine)


def teardown_database():
    Base.metadata.drop_all(bind=engine)


def test_add_product():
    setup_database()

    response = client.post(
        "/products/",
        json={
            "name": "Integration Laptop",
            "category": "Laptop",
            "price": 65000.00,
            "quantity": 20,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Integration Laptop"
    assert data["category"] == "Laptop"
    assert Decimal(str(data["price"])) == Decimal("65000.00")
    assert data["quantity"] == 20
    assert "id" in data

    teardown_database()


def test_view_product():
    setup_database()

    create_response = client.post(
        "/products/",
        json={
            "name": "Integration Phone",
            "category": "Smartphone",
            "price": 30000.00,
            "quantity": 15,
        },
    )

    product_id = create_response.json()["id"]

    response = client.get(
        f"/products/{product_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == product_id
    assert data["name"] == "Integration Phone"
    assert data["category"] == "Smartphone"

    teardown_database()


def test_search_products_by_name():
    setup_database()

    client.post(
        "/products/",
        json={
            "name": "Integration Headphones",
            "category": "Headphones",
            "price": 12000.00,
            "quantity": 10,
        },
    )

    response = client.get(
        "/products/?name=Integration"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Integration Headphones"

    teardown_database()


def test_search_products_by_category():
    setup_database()

    client.post(
        "/products/",
        json={
            "name": "Integration Monitor",
            "category": "Monitor",
            "price": 25000.00,
            "quantity": 8,
        },
    )

    response = client.get(
        "/products/?category=Monitor"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["category"] == "Monitor"

    teardown_database()


def test_search_products_by_id():
    setup_database()

    create_response = client.post(
        "/products/",
        json={
            "name": "Integration Keyboard",
            "category": "Accessories",
            "price": 5000.00,
            "quantity": 25,
        },
    )

    product_id = create_response.json()["id"]

    response = client.get(
        f"/products/?product_id={product_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == product_id

    teardown_database()


def test_update_product():
    setup_database()

    create_response = client.post(
        "/products/",
        json={
            "name": "Integration Tablet",
            "category": "Tablet",
            "price": 40000.00,
            "quantity": 10,
        },
    )

    product_id = create_response.json()["id"]

    response = client.put(
        f"/products/{product_id}",
        json={
            "price": 35000.00,
            "quantity": 15,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == product_id
    assert Decimal(str(data["price"])) == Decimal("35000.00")
    assert data["quantity"] == 15

    teardown_database()


def test_delete_product():
    setup_database()

    create_response = client.post(
        "/products/",
        json={
            "name": "Integration Mouse",
            "category": "Accessories",
            "price": 2000.00,
            "quantity": 30,
        },
    )

    product_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/products/{product_id}"
    )

    assert delete_response.status_code == 200

    deleted_data = delete_response.json()

    assert deleted_data["id"] == product_id

    get_response = client.get(
        f"/products/{product_id}"
    )

    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Product not found"

    teardown_database()


def test_view_nonexistent_product():
    setup_database()

    response = client.get(
        "/products/9999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"

    teardown_database()
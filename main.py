from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI()


class ProductCreate(BaseModel):
    name: str
    category: str
    price: int


class UserCreate(BaseModel):
    name: str
    age: int
    email: str
    is_active: bool = True



products = [
    {"id": 1, "name": "iPhone", "category": "phone", "price": 1000},
    {"id": 2, "name": "MacBook", "category": "laptop", "price": 1500},
    {"id": 3, "name": "Samsung", "category": "phone", "price": 800},
    {"id": 4, "name": "Lenovo", "category": "laptop", "price": 700},
]


users = [
    {"id": 1, "name": "Ali", "age": 18},
    {"id": 2, "name": "Umar", "age": 20},
    {"id": 3, "name": "Hasan", "age": 18},
    {"id": 4, "name": "Aziz", "age": 25},
]


@app.get("/check")
async def check_handler():
    return {"message": "ok"}


@app.get("/users")
async def get_users(age: int | None = None):
    if age is not None:
        return [user for user in users if user["age"] == age]
    return users


@app.get("/products")
async def get_products(
    sort_by: Literal["id", "name", "price"] = "id",
    sort_order: Literal["asc", "desc"] = "asc",
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    category: str | None = Query(default=None, min_length=3, max_length=30),
    max_price: int | None = Query(default=None, ge=0),
    min_price: int | None = Query(default=None, ge=0),
    name: str | None = Query(default=None, min_length=2, max_length=50),
):
    result = products

    if category is not None:
        result = [
            product for product in result if product["category"] == category.lower()
        ]

    if max_price is not None:
        result = [product for product in result if product["price"] <= max_price]

    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=400, detail="min_price cannot be greater than max_price"
        )

    if name is not None:
        result = [
            product for product in result if name.lower() in product["name"].lower()
        ]

    result = sorted(
        result, key=lambda product: product[sort_by], reverse=sort_order == "desc"
    )

    return result[offset : offset + limit]


@app.get("/products/{product_id}")
async def get_produtc(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")


@app.post("/products")
async def post_product(product: ProductCreate):
    return product


@app.post('/users')
async def post_user(user: UserCreate):
    return user
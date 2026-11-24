from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI()


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    category: str = Field(min_length=3, max_length=30)
    price: int = Field(ge=0)


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    age: int = Field(ge=18, le=100)
    email: str = Field(min_length=5, max_length=100)
    is_active: bool = Field(default=True)


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

    if min_price is not None:
        result = [product for product in result if product["price"] >= min_price]

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


@app.post("/products", status_code=201)
async def post_product(product: ProductCreate):
    for p in products:
        if p["name"].lower() == product.name.lower():
            raise HTTPException(status_code=409, detail="Product already exists")

    new_product = product.model_dump()

    new_product["id"] = max((p["id"] for p in products), default=0) + 1

    products.append(new_product)

    return new_product


@app.post("/users", status_code=201)
async def post_user(user: UserCreate):

    if any(u.get("email") == user.email for u in users):
        raise HTTPException(status_code=409, detail="Email already exists")

    new_user = user.model_dump()

    new_user["id"] = max((u["id"] for u in users), default=0) + 1

    users.append(new_user)

    return new_user


@app.put("/products/{product_id}")
async def put_product(product_id: int, product: ProductCreate):
    for index, p in enumerate(products):
        if p["id"] == product_id:
            updated_product = product.model_dump()
            updated_product["id"] = product_id

            products[index] = updated_product

            return updated_product

    raise HTTPException(status_code=404, detail="Product not found")


@app.put("/users/{user_id}")
async def put_user(user_id: int, user: UserCreate):
    for index, u in enumerate(users):
        if u["id"] == user_id:
            updated_user = user.model_dump()
            updated_user["id"] = user_id

            users[index] = updated_user

            return updated_user

    raise HTTPException(status_code=404, detail="user not found")

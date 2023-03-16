from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import ValidationError
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Trading App"
)


# Благодаря этой функции клиент видит ошибки, происходящие на сервере, вместо "Internal server error"
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors()}),
    )


@app.get("/")
def hello():
    return "Hello world!"


fake_users = [
    {"id": 1, "role": "admin", "name": "Mike"},
    {"id": 2, "role": "investor", "name": "Julia"},
    {"id": 3, "role": "trader", "name": "Sam"},
    {"id": 4, "role": "investor", "name": "Michael", "degree": [
        {"id": 1, "created_at": "2020-01-05-01T00:20:30", "type_degree": "expert"}
    ]}
]


class DegreeType(Enum):
    newbie = "newbie"
    expert = "expert"


class Degree(BaseModel):
    id: int
    created_at: datetime
    type_degree: DegreeType


class User(BaseModel):
    id: int
    role: str
    name: str
    degree: Optional[List[Degree]] = []


@app.get("/users/{user_id}", response_model=List[User])
def get_user(user_id: int):
    return [user for user in fake_users if user.get("id") == user_id]


fake_trades = [
    {"id": 1, "user_id": 1, "currency": "BTC", "side": "buy", "price": 123, "amount": 2.12},
    {"id": 2, "user_id": 1, "currency": "BTC", "side": "sell", "price": 120, "amount": 1.11},
    {"id": 3, "user_id": 3, "currency": "USDT", "side": "sell", "price": 74, "amount": 0.80},
    {"id": 4, "user_id": 1, "currency": "BNB", "side": "buy", "price": 149, "amount": 1.43},
    {"id": 5, "user_id": 2, "currency": "ETH", "side": "buy", "price": 99, "amount": 3.14},
    {"id": 6, "user_id": 3, "currency": "USDT", "side": "sell", "price": 75, "amount": 0.61},
    {"id": 7, "user_id": 3, "currency": "BTC", "side": "sell", "price": 121, "amount": 2.00},
    {"id": 8, "user_id": 1, "currency": "BUSD", "side": "buy", "price": 100, "amount": 1.21},
    {"id": 9, "user_id": 2, "currency": "BNB", "side": "buy", "price": 151, "amount": 1.50},
    {"id": 10, "user_id": 2, "currency": "BTC", "side": "buy", "price": 129, "amount": 2.22},
]


@app.get("/trades")
def get_trades(limit: int = 2, offset: int = 0):
    return fake_trades[offset:][:limit]


fake_users2 = [
    {"id": 1, "role": "admin", "name": "Mike"},
    {"id": 2, "role": "investor", "name": "Julia"},
    {"id": 3, "role": "trader", "name": "Sam"},
]


@app.post("/users/{user_id}")
def change_user_name(user_id: int, new_name: str):
    current_user = list(filter(lambda user: user.get("id") == user_id, fake_users2))[0]
    current_user["name"] = new_name
    return {"status": 200, "data": current_user}


class Trade(BaseModel):
    id: int
    user_id: int
    currency: str = Field(max_length=5)
    side: str
    price: float = Field(ge=0)
    amount: float


@app.post("/trades")
def add_trades(trades: List[Trade]):
    fake_trades.extend(trades)
    return {"status": 200, "data": fake_trades}

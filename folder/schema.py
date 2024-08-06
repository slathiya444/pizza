# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.CUSTOMER

class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None

class User(UserBase):
    id: int
    role: UserRole
    is_active: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    role: UserRole | None = None

# app/schemas/pizza.py
from pydantic import BaseModel

class PizzaBase(BaseModel):
    name: str
    description: str
    price: float
    is_available: bool = True

class PizzaCreate(PizzaBase):
    pass

class PizzaUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    is_available: bool | None = None

class Pizza(PizzaBase):
    id: int

    class Config:
        orm_mode = True

# app/schemas/order.py
from pydantic import BaseModel
from datetime import datetime
from app.models.order import OrderStatus

class OrderItemBase(BaseModel):
    pizza_id: int
    quantity: int

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    unit_price: float

    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    user_id: int

class OrderCreate(OrderBase):
    items: list[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: OrderStatus

class Order(OrderBase):
    id: int
    total_amount: float
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    items: list[OrderItem]

    class Config:
        orm_mode = True

# app/schemas/cart.py
from pydantic import BaseModel

class CartItemBase(BaseModel):
    pizza_id: int
    quantity: int = 1

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int

class CartItem(CartItemBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

class Cart(BaseModel):
    items: list[CartItem]
    total: float

    class Config:
        orm_mode = True
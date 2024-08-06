# app/crud/user.py
from typing import Optional
from sqlalchemy.orm import Session
from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            username=obj_in.username,
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            role=obj_in.role
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, username: str, password: str) -> Optional[User]:
        user = self.get_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

user = CRUDUser(User)

# app/crud/pizza.py
from app.crud.base import CRUDBase
from app.models.pizza import Pizza
from app.schemas.pizza import PizzaCreate, PizzaUpdate

class CRUDPizza(CRUDBase[Pizza, PizzaCreate, PizzaUpdate]):
    pass

pizza = CRUDPizza(Pizza)

# app/crud/order.py
from typing import List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.order import Order, OrderItem
from app.schemas.order import OrderCreate, OrderUpdate

class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    def create_with_items(self, db: Session, *, obj_in: OrderCreate, user_id: int) -> Order:
        db_obj = Order(user_id=user_id, total_amount=0)
        for item in obj_in.items:
            order_item = OrderItem(**item.dict(), order=db_obj)
            db.add(order_item)
            db_obj.total_amount += order_item.unit_price * order_item.quantity
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_user_orders(self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        return db.query(Order).filter(Order.user_id == user_id).offset(skip).limit(limit).all()

order = CRUDOrder(Order)

# app/crud/cart.py
from typing import List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.cart import CartItem
from app.schemas.cart import CartItemCreate, CartItemUpdate

class CRUDCart(CRUDBase[CartItem, CartItemCreate, CartItemUpdate]):
    def get_user_cart(self, db: Session, *, user_id: int) -> List[CartItem]:
        return db.query(CartItem).filter(CartItem.user_id == user_id).all()

    def add_to_cart(self, db: Session, *, user_id: int, pizza_id: int, quantity: int = 1) -> CartItem:
        cart_item = db.query(CartItem).filter(
            CartItem.user_id == user_id,
            CartItem.pizza_id == pizza_id
        ).first()

        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(user_id=user_id, pizza_id=pizza_id, quantity=quantity)
            db.add(cart_item)

        db.commit()
        db.refresh(cart_item)
        return cart_item

    def remove_from_cart(self, db: Session, *, user_id: int, pizza_id: int) -> None:
        db.query(CartItem).filter(
            CartItem.user_id == user_id,
            CartItem.pizza_id == pizza_id
        ).delete()
        db.commit()

    def clear_cart(self, db: Session, *, user_id: int) -> None:
        db.query(CartItem).filter(CartItem.user_id == user_id).delete()
        db.commit()

cart = CRUDCart(CartItem)
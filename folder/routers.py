# app/routers/auth.py
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from app.database import get_db

router = APIRouter(tags=["authentication"])

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    user = crud.user.authenticate(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.username, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/users", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.user.get_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.user.create(db=db, obj_in=user)

# app/routers/admin.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.database import get_db
from app.dependencies import get_current_active_admin

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/pizzas", response_model=schemas.Pizza)
def create_pizza(
    pizza: schemas.PizzaCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_admin)
):
    return crud.pizza.create(db=db, obj_in=pizza)

@router.put("/pizzas/{pizza_id}", response_model=schemas.Pizza)
def update_pizza(
    pizza_id: int,
    pizza: schemas.PizzaUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_admin)
):
    db_pizza = crud.pizza.get(db=db, id=pizza_id)
    if not db_pizza:
        raise HTTPException(status_code=404, detail="Pizza not found")
    return crud.pizza.update(db=db, db_obj=db_pizza, obj_in=pizza)

@router.delete("/pizzas/{pizza_id}", response_model=schemas.Pizza)
def delete_pizza(
    pizza_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_admin)
):
    db_pizza = crud.pizza.get(db=db, id=pizza_id)
    if not db_pizza:
        raise HTTPException(status_code=404, detail="Pizza not found")
    return crud.pizza.remove(db=db, id=pizza_id)

@router.put("/orders/{order_id}/status", response_model=schemas.Order)
def update_order_status(
    order_id: int,
    status: schemas.OrderUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_admin)
):
    db_order = crud.order.get(db=db, id=order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return crud.order.update(db=db, db_obj=db_order, obj_in=status)

# app/routers/customer.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.database import get_db
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/customer", tags=["customer"])

@router.get("/pizzas", response_model=list[schemas.Pizza])
def get_pizzas(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    return crud.pizza.get_multi(db, skip=skip, limit=limit)

@router.post("/cart/add", response_model=schemas.CartItem)
def add_to_cart(
    item: schemas.CartItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    return crud.cart.add_to_cart(db, user_id=current_user.id, pizza_id=item.pizza_id, quantity=item.quantity)

@router.delete("/cart/remove/{pizza_id}")
def remove_from_cart(
    pizza_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    crud.cart.remove_from_cart(db, user_id=current_user.id, pizza_id=pizza_id)
    return {"message": "Item removed from cart"}

@router.get("/cart", response_model=list[schemas.CartItem])
def get_cart(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    return crud.cart.get_user_cart(db, user_id=current_user.id)

@router.post("/orders", response_model=schemas.Order)
def create_order(
    order: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    return crud.order.create_with_items(db, obj_in=order, user_id=current_user.id)

@router.get("/orders", response_model=list[schemas.Order])
def get_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    return crud.order.get_user_orders(db, user_id=current_user.id, skip=skip, limit=limit)

# app/routers/delivery.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.database import get_db
from app.dependencies import get_current_active_delivery_partner

router = APIRouter(prefix="/delivery", tags=["delivery"])

@router.put("/orders/{order_id}/status", response_model=schemas.Order)
def update_order_status(
    order_id: int,
    status: schemas.OrderUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_delivery_partner)
):
    db_order = crud.order.get(db=db, id=order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return crud.order.update(db=db, db_obj=db_order, obj_in=status)

@router.post("/orders/{order_id}/comment", response_model=schemas.Order)
def add_order_comment(
    order_id: int,
    comment: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_delivery_partner)
):
    db_order = crud.order.get(db=db, id=order_id)
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    # Assuming you have a 'comment' field in your Order model
    return crud.order.update(db=db, db_obj=db_order, obj_in={"comment": comment})
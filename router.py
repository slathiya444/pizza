# app/routers/admin.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas, crud
from app.dependencies import get_current_active_admin

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/pizzas", response_model=schemas.Pizza)
async def create_pizza(
    pizza: schemas.PizzaCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_admin)
):
    return crud.pizza.create(db=db, pizza=pizza)

# app/routers/customer.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas, crud
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/customer", tags=["customer"])

@router.get("/pizzas", response_model=list[schemas.Pizza])
async def get_pizzas(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    return crud.pizza.get_all(db=db)
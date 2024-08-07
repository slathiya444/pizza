# api/customer.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from .models import Order, OrderItem, Pizza  # Ensure you have the Order and OrderItem models defined
from .schemas import OrderCreate, Order, OrderItemCreate
from .dependencies import get_current_user

router = APIRouter()


@router.post("/orders", response_model=Order)
async def create_order(order_create: OrderCreate, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    # Calculate total amount and validate pizzas
    total_amount = 0
    order_items = []

    for item in order_create.items:
        # Check if the pizza exists
        db_pizza = db.query(Pizza).filter(Pizza.id == item.pizza_id).first()
        if not db_pizza:
            raise HTTPException(status_code=404, detail=f"Pizza with id {item.pizza_id} not found")

        # Calculate the total amount
        total_amount += db_pizza.price * item.quantity

        # Create order item
        order_item = OrderItem(
            pizza_id=item.pizza_id,
            quantity=item.quantity,
            unit_price=db_pizza.price
        )
        order_items.append(order_item)

    # Create the order
    new_order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        order_items=order_items  # This will create the relationship
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order


@router.get("/orders", response_model=list[Order])
async def get_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Retrieve all orders for the current user
    orders = db.query(Order).filter(Order.user_id == current_user.id).all()
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found for this user")

    return orders

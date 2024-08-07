# api/customer.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from .models import CartItem, Pizza  # Ensure you have the CartItem model defined
from .schemas import CartItemCreate, CartItemUpdate, Cart, CartItem
from .dependencies import get_current_user

router = APIRouter()

@router.post("/cart", response_model=CartItem)
async def add_to_cart(cart_item: CartItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Check if the pizza exists
    db_pizza = db.query(Pizza).filter(Pizza.id == cart_item.pizza_id).first()
    if not db_pizza:
        raise HTTPException(status_code=404, detail="Pizza not found")

    # Check if the cart item already exists for the user
    existing_item = db.query(CartItem).filter(CartItem.user_id == current_user.id, CartItem.pizza_id == cart_item.pizza_id).first()
    if existing_item:
        # Update the quantity if the item already exists
        existing_item.quantity += cart_item.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item
    else:
        # Create a new cart item
        new_item = CartItem(user_id=current_user.id, pizza_id=cart_item.pizza_id, quantity=cart_item.quantity)
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item

@router.put("/cart/{item_id}", response_model=CartItem)
async def update_cart(item_id: int, cart_item_update: CartItemUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Find the cart item to update
    item_to_update = db.query(CartItem).filter(CartItem.id == item_id, CartItem.user_id == current_user.id).first()
    if not item_to_update:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    # Update the quantity
    item_to_update.quantity = cart_item_update.quantity
    db.commit()
    db.refresh(item_to_update)
    return item_to_update

@router.get("/cart", response_model=Cart)
async def view_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Retrieve the user's cart items
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    if not cart_items:
        raise HTTPException(status_code=404, detail="Cart not found")

    # Calculate the total price
    total = sum(item.quantity * item.pizza.price for item in cart_items)  # Assuming Pizza model has a price attribute
    return Cart(items=cart_items, total=total)

# api/delivery_person.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from .models import Order  # Ensure you have the Order model defined
from .schemas import DeliveryStatusUpdate  # Assuming you have a DeliveryStatusUpdate schema defined
from .dependencies import get_current_delivery_person  # Assuming you have a dependency to get the current delivery person

# delivery model
# models/delivery_comment.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class DeliveryComment(Base):
    __tablename__ = "delivery_comments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    delivery_person_id = Column(Integer, ForeignKey("delivery_persons.id"), nullable=False)  # Assuming you have a delivery_persons table
    comment = Column(String, nullable=False)

    order = relationship("Order", back_populates="delivery_comments")  # Relationship to the Order model
    delivery_person = relationship("DeliveryPerson")  # Assuming you have a DeliveryPerson model



router = APIRouter()
# Update delivery status endpoint
@router.put("/deliveries/{order_id}/status", response_model=Order)
async def update_delivery_status(order_id: int, status_update: DeliveryStatusUpdate, db: Session = Depends(get_db), current_delivery_person: DeliveryPerson = Depends(get_current_delivery_person)):
    # Find the order to update
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Update the delivery status
    order.status = status_update.status
    db.commit()
    db.refresh(order)
    return order

# add delivery comment end point
# api/delivery_person.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from .models import Order, DeliveryComment  # Ensure you have the Order and DeliveryComment models defined
from .schemas import DeliveryCommentCreate  # Assuming you have a DeliveryCommentCreate schema defined
from .dependencies import get_current_delivery_person  # Assuming you have a dependency to get the current delivery person

router = APIRouter()

# Previous endpoint...

@router.post("/deliveries/{order_id}/comments", response_model=DeliveryComment)
async def add_delivery_comment(order_id: int, comment_create: DeliveryCommentCreate, db: Session = Depends(get_db), current_delivery_person: DeliveryPerson = Depends(get_current_delivery_person)):
    # Find the order
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Create the delivery comment
    new_comment = DeliveryComment(
        order_id=order.id,
        delivery_person_id=current_delivery_person.id,
        comment=comment_create.comment
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

# Schema
# schemas/schema_delivery.py
from pydantic import BaseModel
from app.models.order import OrderStatus

class DeliveryStatusUpdate(BaseModel):
    status: OrderStatus

class DeliveryCommentCreate(BaseModel):
    comment: str


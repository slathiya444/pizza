# app/main.py
from fastapi import FastAPI
from app.routers import auth, admin, customer, delivery
from app.database import engine
from app import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pizza Delivery API")

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(customer.router)
app.include_router(delivery.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Pizza Delivery API"}
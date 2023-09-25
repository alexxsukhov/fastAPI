from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from databases import Database
from datetime import datetime

DATABASE_URL = "sqlite:///./test.db"
database = Database(DATABASE_URL)
metadata = declarative_base()

app = FastAPI()


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str


class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float


class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float


class OrderCreate(BaseModel):
    user_id: int
    product_id: int


class Order(BaseModel):
    id: int
    user_id: int
    product_id: int
    date: datetime
    status: str


class UserDB(metadata):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    orders = relationship("OrderDB", back_populates="user")


class ProductDB(metadata):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Integer)


class OrderDB(metadata):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="created")
    user = relationship("UserDB", back_populates="orders")
    product = relationship("ProductDB")


@app.on_event("startup")
async def startup():
    await database.connect()
    engine = create_engine(DATABASE_URL)
    metadata.metadata.create_all(bind=engine)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    app.state.db = session_local()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    app.state.db.close()


@app.post("/users/", response_model=User)
async def create_user(user: UserCreate):
    query = UserDB(**user.dict())
    app.state.db.add(query)
    app.state.db.commit()
    app.state.db.refresh(query)
    return query


@app.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int):
    query = app.state.db.query(UserDB).filter(UserDB.id == user_id).first()
    if query is None:
        raise HTTPException(status_code=404, detail="User not found")
    return query


@app.post("/products/", response_model=Product)
async def create_product(product: ProductCreate):
    query = ProductDB(**product.dict())
    app.state.db.add(query)
    app.state.db.commit()
    app.state.db.refresh(query)
    return query


@app.get("/products/{product_id}", response_model=Product)
async def read_product(product_id: int):
    query = app.state.db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if query is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return query


@app.post("/orders/", response_model=Order)
async def create_order(order: OrderCreate):
    user = app.state.db.query(UserDB).filter(UserDB.id == order.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    product = app.state.db.query(ProductDB).filter(ProductDB.id == order.product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    query = OrderDB(**order.dict())
    app.state.db.add(query)
    app.state.db.commit()
    app.state.db.refresh(query)
    return query


@app.get("/orders/{order_id}", response_model=Order)
async def read_order(order_id: int):
    query = app.state.db.query(OrderDB).filter(OrderDB.id == order_id).first()
    if query is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return query

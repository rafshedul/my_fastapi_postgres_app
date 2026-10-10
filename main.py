from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from pydantic import BaseModel


DATABASE_URL = "postgresql+psycopg2://postgres:1122@localhost:5432/fastapi_db"

engine = create_engine(DATABASE_URL)

Base = declarative_base()


# ------------------
# FastAPI App
# ------------------

app = FastAPI()


# ------------------
# User Model
# ------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)


# ------------------
# Category Model
# ------------------

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)


# ------------------
# Product Model
# ------------------

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))


# ------------------
# Create Tables
# ------------------

Base.metadata.create_all(engine)


# ------------------
# Database Session
# ------------------

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ------------------
# Pydantic Schemas
# ------------------

class CategoryCreate(BaseModel):
    name: str


class CategoryResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    name: str
    email: str
    phone: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    name: str
    price: int
    category_id: int


class ProductUpdate(BaseModel):
    name: str
    price: int
    category_id: int


class ProductResponse(BaseModel):
    id: int
    name: str
    price: int
    category_id: int

    class Config:
        from_attributes = True


# ------------------
# User API
# ------------------

@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db=Depends(get_db)):

    new_user = User(
        name=user.name,
        email=user.email,
        phone=user.phone
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# ------------------
# User List API
# ------------------

@app.get("/users/", response_model=list[UserResponse])
def get_users(db=Depends(get_db)):

    users = db.query(User).all()

    return users

# ------------------
# User Details API
# ------------------

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db=Depends(get_db)):

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user
# ------------------
# User Delete API
# ------------------

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db=Depends(get_db)):

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}
# ------------------
# Category Create API
# ------------------

@app.post("/categories/", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db=Depends(get_db)):

    new_category = Category(
        name=category.name
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category


# ------------------
# Category List API
# ------------------

@app.get("/categories/", response_model=list[CategoryResponse])
def get_categories(db=Depends(get_db)):

    categories = db.query(Category).all()

    return categories


# ------------------
# Category Details API
# ------------------

@app.get("/categories/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db=Depends(get_db)):

    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return category


# ------------------
# Category Update API
# ------------------

@app.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category: CategoryCreate,
    db=Depends(get_db)
):

    existing_category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if not existing_category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    existing_category.name = category.name

    db.commit()
    db.refresh(existing_category)

    return existing_category
# ------------------
# Category Delete API
# ------------------

@app.delete("/categories/{category_id}")
def delete_category(category_id: int, db=Depends(get_db)):

    category = db.query(Category).filter(
        Category.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    db.delete(category)
    db.commit()

    return {"message": "Category deleted successfully"}

# ------------------
# Product Create API
# ------------------

@app.post("/products/", response_model=ProductResponse)
def create_product(product: ProductCreate, db=Depends(get_db)):

    category = db.query(Category).filter(
        Category.id == product.category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    new_product = Product(
        name=product.name,
        price=product.price,
        category_id=product.category_id
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


# ------------------
# Product List API
# ------------------

@app.get("/products/", response_model=list[ProductResponse])
def get_products(db=Depends(get_db)):

    products = db.query(Product).all()

    return products


# ------------------
# Product Details API
# ------------------

@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db=Depends(get_db)):

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product


# ------------------
# Product Update API
# ------------------

@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db=Depends(get_db)
):

    existing_product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not existing_product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    # Step 26: Check Category
    category = db.query(Category).filter(
        Category.id == product.category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    existing_product.name = product.name
    existing_product.price = product.price
    existing_product.category_id = product.category_id

    db.commit()
    db.refresh(existing_product)

    return existing_product


# ------------------
# Product Delete API
# ------------------

@app.delete("/products/{product_id}")
def delete_product(product_id: int, db=Depends(get_db)):

    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}
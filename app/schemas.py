from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0
    sku: str
    category: str
    image_url: Optional[str] = None
    color_url: Optional[str] = None
    displacement_url: Optional[str] = None
    is_active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    color_url: Optional[str] = None
    displacement_url: Optional[str] = None
    is_active: Optional[bool] = None


class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CartItemBase(BaseModel):
    product_id: int
    quantity: int = 1


class CartItemCreate(CartItemBase):
    pass


class CartItem(CartItemBase):
    id: int
    cart_id: int
    added_at: datetime
    product: Product

    class Config:
        from_attributes = True


class CartCreate(BaseModel):
    user_id: str


class Cart(BaseModel):
    id: int
    user_id: str
    items: List[CartItem]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CartSummary(BaseModel):
    total_items: int
    total_price: float
    items: List[CartItem]


class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    price_at_purchase: float


class OrderItemCreate(OrderItemBase):
    pass


class OrderItem(OrderItemBase):
    id: int
    order_id: int
    product: Product

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    customer_name: str
    customer_email: str
    customer_phone: str
    shipping_address: str
    items: List[OrderItemCreate]


class Order(BaseModel):
    id: int
    user_id: str
    status: str
    total_price: float
    customer_name: str
    customer_email: str
    customer_phone: str
    shipping_address: str
    items: List[OrderItem]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    sub: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None


class GoogleLogin(BaseModel):
    id_token: str

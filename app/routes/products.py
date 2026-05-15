from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.controllers.product_controller import ProductController
from app.schemas import ProductCreate, ProductUpdate
from app.services.auth_service import get_current_admin

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("/", response_model=dict)
async def list_products(
    db: AsyncSession = Depends(get_db),
    category: str = Query(None),
    search: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List all products with optional filtering"""
    controller = ProductController(db)
    return await controller.get_products(category=category, search=search, skip=skip, limit=limit)


@router.get("/categories", response_model=dict)
async def list_categories(db: AsyncSession = Depends(get_db)):
    """Get all unique product categories"""
    controller = ProductController(db)
    return await controller.get_product_categories()


@router.get("/{product_id}", response_model=dict)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific product by ID"""
    controller = ProductController(db)
    return await controller.get_product(product_id)


@router.post("/", response_model=dict)
async def create_product(
    product: ProductCreate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    """Create a new product (admin only in production)"""
    controller = ProductController(db)
    return await controller.create_product(product)


@router.put("/{product_id}", response_model=dict)
async def update_product(
    product_id: int,
    product: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    """Update a product (admin only in production)"""
    controller = ProductController(db)
    return await controller.update_product(product_id, product)


@router.delete("/{product_id}", response_model=dict)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    """Delete a product (admin only in production)"""
    controller = ProductController(db)
    return await controller.delete_product(product_id)

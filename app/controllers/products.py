from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas import Product as ProductSchema, ProductCreate, ProductUpdate
from app.services.product_service import ProductService

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("/", response_model=List[ProductSchema])
def list_products(
    db: Session = Depends(get_db),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """List all products with optional filtering"""
    try:
        service = ProductService(db)
        products = service.get_products(
            category=category,
            search=search,
            skip=skip,
            limit=limit
        )
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving products: {str(e)}")


@router.get("/categories", response_model=List[str])
def list_categories(db: Session = Depends(get_db)):
    """Get all unique product categories"""
    try:
        service = ProductService(db)
        categories = service.get_product_categories()
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving categories: {str(e)}")


@router.get("/{product_id}", response_model=ProductSchema)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product by ID"""
    try:
        service = ProductService(db)
        product = service.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving product: {str(e)}")


@router.post("/", response_model=ProductSchema, status_code=201)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product"""
    try:
        service = ProductService(db)
        new_product = service.create_product(product)
        return new_product
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating product: {str(e)}")


@router.put("/{product_id}", response_model=ProductSchema)
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    """Update an existing product"""
    try:
        service = ProductService(db)
        updated_product = service.update_product(product_id, product)
        if not updated_product:
            raise HTTPException(status_code=404, detail="Product not found")
        return updated_product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating product: {str(e)}")


@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product (soft delete)"""
    try:
        service = ProductService(db)
        success = service.delete_product(product_id)
        if not success:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"message": "Product deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting product: {str(e)}")
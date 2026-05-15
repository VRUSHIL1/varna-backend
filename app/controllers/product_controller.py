from fastapi import HTTPException, Query
from typing import List, Optional
from app.services.product_service import ProductService
from app.schemas import Product as ProductSchema, ProductCreate, ProductUpdate
from app.database import AsyncSession


class ProductController:
    def __init__(self, db: AsyncSession):
        self.service = ProductService(db)

    async def get_products(
        self,
        category: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = Query(0, ge=0),
        limit: int = Query(50, ge=1, le=100),
    ) -> dict:
        """Get all products with optional filtering"""
        try:
            products = await self.service.get_products(
                category=category,
                search=search,
                skip=skip,
                limit=limit
            )
            return {
                "success": True,
                "message": "Products retrieved successfully",
                "data": products,
                "count": len(products)
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve products: {str(e)}")

    async def get_product_categories(self) -> dict:
        """Get all unique product categories"""
        try:
            categories = await self.service.get_product_categories()
            return {
                "success": True,
                "message": "Categories retrieved successfully",
                "data": categories
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve categories: {str(e)}")

    async def get_product(self, product_id: int) -> dict:
        """Get a specific product by ID"""
        try:
            product = await self.service.get_product_by_id(product_id)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")

            return {
                "success": True,
                "message": "Product retrieved successfully",
                "data": product
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve product: {str(e)}")

    async def create_product(self, product: ProductCreate) -> dict:
        """Create a new product"""
        try:
            # Check if SKU already exists
            existing = await self.service.get_product_by_sku(product.sku)
            if existing:
                raise HTTPException(status_code=400, detail="SKU already exists")

            created_product = await self.service.create_product(product)
            return {
                "success": True,
                "message": "Product created successfully",
                "data": created_product
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create product: {str(e)}")

    async def update_product(self, product_id: int, product: ProductUpdate) -> dict:
        """Update a product"""
        try:
            updated_product = await self.service.update_product(product_id, product)
            if not updated_product:
                raise HTTPException(status_code=404, detail="Product not found")

            return {
                "success": True,
                "message": "Product updated successfully",
                "data": updated_product
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update product: {str(e)}")

    async def delete_product(self, product_id: int) -> dict:
        """Delete a product"""
        try:
            success = await self.service.delete_product(product_id)
            if not success:
                raise HTTPException(status_code=404, detail="Product not found")

            return {
                "success": True,
                "message": "Product deleted successfully"
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete product: {str(e)}")
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Optional
from app.models import Product
from app.schemas import ProductCreate, ProductUpdate


class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_products(
        self,
        category: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Product]:
        """Get all active products with optional filtering"""
        query = select(Product).where(Product.is_active == True)

        if category:
            query = query.where(Product.category == category)

        if search:
            query = query.where(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%")
                )
            )

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_product_categories(self) -> List[str]:
        """Get all unique product categories"""
        query = select(Product.category).where(Product.is_active == True).distinct()
        result = await self.db.execute(query)
        categories = result.scalars().all()
        return [cat for cat in categories]

    async def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Get a specific product by ID"""
        query = select(Product).where(Product.id == product_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_product_by_sku(self, sku: str) -> Optional[Product]:
        """Get a specific product by SKU"""
        query = select(Product).where(Product.sku == sku)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_product(self, product_data: ProductCreate) -> Product:
        """Create a new product"""
        product = Product(**product_data.model_dump())
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def update_product(self, product_id: int, product_data: ProductUpdate) -> Optional[Product]:
        """Update an existing product"""
        product = await self.get_product_by_id(product_id)
        if not product:
            return None

        update_data = product_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)

        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def delete_product(self, product_id: int) -> bool:
        """Soft delete a product (set is_active to False)"""
        product = await self.get_product_by_id(product_id)
        if not product:
            return False

        product.is_active = False
        self.db.add(product)
        await self.db.commit()
        return True

    async def check_product_stock(self, product_id: int, quantity: int) -> tuple[bool, Optional[Product]]:
        """Check if product has sufficient stock"""
        product = await self.get_product_by_id(product_id)
        if not product:
            return False, None

        return product.stock >= quantity, product
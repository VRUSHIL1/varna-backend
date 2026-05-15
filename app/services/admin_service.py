from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Product, Order, OrderItem


class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # User Management
    async def list_users(self, skip: int = 0, limit: int = 50, search: str = None) -> dict:
        """List all users with optional search"""
        query = select(User)
        
        if search:
            query = query.where(User.email.ilike(f"%{search}%") | User.full_name.ilike(f"%{search}%"))
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        users = result.scalars().all()
        
        # Get total count
        count_query = select(func.count(User.id))
        if search:
            count_query = count_query.where(User.email.ilike(f"%{search}%") | User.full_name.ilike(f"%{search}%"))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        return {
            "users": [
                {
                    "id": u.id,
                    "email": u.email,
                    "full_name": u.full_name,
                    "role": u.role,
                    "is_active": u.is_active,
                    "created_at": u.created_at,
                }
                for u in users
            ],
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    async def update_user_role(self, user_id: int, role: str) -> Optional[User]:
        """Update user role (admin/user)"""
        if role not in ["admin", "user"]:
            raise ValueError("Invalid role. Must be 'admin' or 'user'")
        
        user = await self._get_user_by_id(user_id)
        if not user:
            return None
        
        user.role = role
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def deactivate_user(self, user_id: int) -> Optional[User]:
        """Deactivate a user account"""
        user = await self._get_user_by_id(user_id)
        if not user:
            return None
        
        user.is_active = False
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def activate_user(self, user_id: int) -> Optional[User]:
        """Activate a user account"""
        user = await self._get_user_by_id(user_id)
        if not user:
            return None
        
        user.is_active = True
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    # Order Management
    async def get_all_orders(self, skip: int = 0, limit: int = 50, status: str = None) -> dict:
        """Get all orders across all users"""
        query = select(Order)
        
        if status:
            query = query.where(Order.status == status)
        
        query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        orders = result.scalars().all()
        
        # Get total count
        count_query = select(func.count(Order.id))
        if status:
            count_query = count_query.where(Order.status == status)
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        return {
            "orders": [self._serialize_order(o) for o in orders],
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    async def get_order_by_id(self, order_id: int) -> Optional[dict]:
        """Get a specific order with items"""
        query = select(Order).where(Order.id == order_id)
        result = await self.db.execute(query)
        order = result.scalar_one_or_none()
        
        if not order:
            return None
        
        return self._serialize_order(order)

    # Dashboard Stats
    async def get_dashboard_stats(self) -> dict:
        """Get admin dashboard statistics"""
        # Total revenue
        revenue_query = select(func.sum(Order.total_price)).where(Order.status.in_(["confirmed", "shipped", "delivered"]))
        revenue_result = await self.db.execute(revenue_query)
        total_revenue = revenue_result.scalar() or 0

        # Order counts by status
        status_query = select(Order.status, func.count(Order.id)).group_by(Order.status)
        status_result = await self.db.execute(status_query)
        order_counts = dict(status_result.all())

        # Low stock products
        low_stock_query = select(Product).where(Product.stock < 5).order_by(Product.stock)
        low_stock_result = await self.db.execute(low_stock_query)
        low_stock = low_stock_result.scalars().all()

        # Total users
        users_query = select(func.count(User.id))
        users_result = await self.db.execute(users_query)
        total_users = users_result.scalar()

        # Total products
        products_query = select(func.count(Product.id))
        products_result = await self.db.execute(products_query)
        total_products = products_result.scalar()

        return {
            "total_revenue": float(total_revenue),
            "order_stats": order_counts,
            "total_orders": sum(order_counts.values()),
            "low_stock_products": [
                {
                    "id": p.id,
                    "name": p.name,
                    "sku": p.sku,
                    "stock": p.stock,
                    "price": p.price,
                }
                for p in low_stock
            ],
            "total_users": total_users,
            "total_products": total_products,
        }

    # Helper methods
    async def _get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    def _serialize_order(self, order: Order) -> dict:
        """Serialize order to dict"""
        return {
            "id": order.id,
            "user_id": order.user_id,
            "status": order.status,
            "total_price": order.total_price,
            "customer_name": order.customer_name,
            "customer_email": order.customer_email,
            "customer_phone": order.customer_phone,
            "shipping_address": order.shipping_address,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            "items": [
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "price_at_purchase": item.price_at_purchase,
                    "product_name": item.product.name if item.product else "Unknown",
                }
                for item in order.items
            ] if order.items else [],
        }

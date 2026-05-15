from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List, Optional
from app.models import Order, OrderItem, Product
from app.schemas import OrderCreate, OrderItemCreate


class OrderService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(self, order_data: OrderCreate, user_id: str) -> Order:
        """Create a new order from cart items"""
        # Validate products exist and calculate total
        total_price = 0.0
        order_items_data = []

        for order_item in order_data.items:
            query = select(Product).where(Product.id == order_item.product_id)
            result = await self.db.execute(query)
            product = result.scalar_one_or_none()
            if not product:
                raise ValueError(f"Product {order_item.product_id} not found")

            # Check stock
            if product.stock < order_item.quantity:
                raise ValueError(f"Insufficient stock for {product.name}")

            total_price += product.price * order_item.quantity
            order_items_data.append((product, order_item.quantity))

        # Create order
        db_order = Order(
            user_id=user_id,
            customer_name=order_data.customer_name,
            customer_email=order_data.customer_email,
            customer_phone=order_data.customer_phone,
            shipping_address=order_data.shipping_address,
            total_price=total_price,
            status="pending"
        )
        self.db.add(db_order)
        await self.db.flush()  # Get the order ID

        # Add order items and reduce stock
        for product, quantity in order_items_data:
            db_order_item = OrderItem(
                order_id=db_order.id,
                product_id=product.id,
                quantity=quantity,
                price_at_purchase=product.price
            )
            self.db.add(db_order_item)

            # Reduce stock
            product.stock -= quantity
            self.db.add(product)

        await self.db.commit()
        await self.db.refresh(db_order)
        return db_order

    async def get_user_orders(self, user_id: str) -> List[Order]:
        """Get all orders for a user"""
        query = select(Order).where(Order.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """Get a specific order by ID"""
        query = select(Order).where(Order.id == order_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_order_status(self, order_id: int, status: str) -> Optional[Order]:
        """Update order status"""
        valid_statuses = ["pending", "confirmed", "shipped", "delivered", "cancelled"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")

        order = await self.get_order_by_id(order_id)
        if not order:
            return None

        order.status = status
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def cancel_order(self, order_id: int) -> Optional[Order]:
        """Cancel an order and restore stock"""
        order = await self.get_order_by_id(order_id)
        if not order:
            return None

        if order.status in ["shipped", "delivered"]:
            raise ValueError("Cannot cancel order that has been shipped or delivered")

        # Restore stock
        for item in order.items:
            item.product.stock += item.quantity
            self.db.add(item.product)

        order.status = "cancelled"
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        return order
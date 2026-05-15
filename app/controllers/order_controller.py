from fastapi import HTTPException
from typing import List
from app.services.order_service import OrderService
from app.schemas import OrderCreate
from app.database import AsyncSession


class OrderController:
    def __init__(self, db: AsyncSession):
        self.service = OrderService(db)

    async def create_order(self, order: OrderCreate, user_id: str) -> dict:
        """Create a new order"""
        try:
            created_order = await self.service.create_order(order, user_id)
            return {
                "success": True,
                "message": "Order created successfully",
                "data": created_order
            }
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")

    async def get_user_orders(self, user_id: str) -> dict:
        """Get all orders for a user"""
        try:
            orders = await self.service.get_user_orders(user_id)
            return {
                "success": True,
                "message": "Orders retrieved successfully",
                "data": orders,
                "count": len(orders)
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve orders: {str(e)}")

    async def get_order(self, order_id: int, current_user) -> dict:
        """Get a specific order"""
        try:
            order = await self.service.get_order_by_id(order_id)
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")

            if current_user.role != "admin" and order.user_id != str(current_user.id):
                raise HTTPException(status_code=403, detail="Forbidden")

            return {
                "success": True,
                "message": "Order retrieved successfully",
                "data": order
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve order: {str(e)}")

    async def update_order_status(self, order_id: int, status: str) -> dict:
        """Update order status"""
        try:
            updated_order = await self.service.update_order_status(order_id, status)
            if not updated_order:
                raise HTTPException(status_code=404, detail="Order not found")

            return {
                "success": True,
                "message": "Order status updated successfully",
                "data": updated_order
            }
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update order status: {str(e)}")

    async def cancel_order(self, order_id: int, current_user) -> dict:
        """Cancel an order"""
        try:
            order = await self.service.get_order_by_id(order_id)
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")

            if current_user.role != "admin" and order.user_id != str(current_user.id):
                raise HTTPException(status_code=403, detail="Forbidden")

            cancelled_order = await self.service.cancel_order(order_id)
            if not cancelled_order:
                raise HTTPException(status_code=404, detail="Order not found")

            return {
                "success": True,
                "message": "Order cancelled successfully",
                "data": cancelled_order
            }
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to cancel order: {str(e)}")
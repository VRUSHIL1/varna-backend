from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.admin_service import AdminService


class AdminController:
    def __init__(self, db: AsyncSession):
        self.service = AdminService(db)

    # User Management
    async def list_users(self, skip: int = 0, limit: int = 50, search: str = None) -> dict:
        """List all users"""
        try:
            result = await self.service.list_users(skip=skip, limit=limit, search=search)
            return {
                "success": True,
                "message": "Users retrieved successfully",
                "data": result
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve users: {str(e)}")

    async def update_user_role(self, user_id: int, role: str) -> dict:
        """Update user role"""
        try:
            user = await self.service.update_user_role(user_id, role)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            return {
                "success": True,
                "message": f"User role updated to {role}",
                "data": {
                    "id": user.id,
                    "email": user.email,
                    "role": user.role,
                }
            }
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update user role: {str(e)}")

    async def deactivate_user(self, user_id: int) -> dict:
        """Deactivate a user"""
        try:
            user = await self.service.deactivate_user(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            return {
                "success": True,
                "message": "User deactivated successfully",
                "data": {
                    "id": user.id,
                    "email": user.email,
                    "is_active": user.is_active,
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to deactivate user: {str(e)}")

    async def activate_user(self, user_id: int) -> dict:
        """Activate a user"""
        try:
            user = await self.service.activate_user(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            return {
                "success": True,
                "message": "User activated successfully",
                "data": {
                    "id": user.id,
                    "email": user.email,
                    "is_active": user.is_active,
                }
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to activate user: {str(e)}")

    # Order Management
    async def get_all_orders(self, skip: int = 0, limit: int = 50, status: str = None) -> dict:
        """Get all orders"""
        try:
            result = await self.service.get_all_orders(skip=skip, limit=limit, status=status)
            return {
                "success": True,
                "message": "Orders retrieved successfully",
                "data": result
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve orders: {str(e)}")

    async def get_order(self, order_id: int) -> dict:
        """Get a specific order"""
        try:
            order = await self.service.get_order_by_id(order_id)
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            
            return {
                "success": True,
                "message": "Order retrieved successfully",
                "data": order
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve order: {str(e)}")

    # Dashboard
    async def get_stats(self) -> dict:
        """Get dashboard statistics"""
        try:
            stats = await self.service.get_dashboard_stats()
            return {
                "success": True,
                "message": "Dashboard stats retrieved successfully",
                "data": stats
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve stats: {str(e)}")

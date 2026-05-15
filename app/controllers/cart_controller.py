from fastapi import HTTPException
from typing import Optional
from app.services.cart_service import CartService
from app.schemas import CartItemCreate, CartSummary
from app.database import AsyncSession


class CartController:
    def __init__(self, db: AsyncSession):
        self.service = CartService(db)

    async def get_cart(self, user_id: str) -> dict:
        """Get cart for a user"""
        try:
            cart = await self.service.get_or_create_cart(user_id)
            return {
                "success": True,
                "message": "Cart retrieved successfully",
                "data": cart
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve cart: {str(e)}")

    async def get_cart_summary(self, user_id: str) -> dict:
        """Get cart summary with total price and item count"""
        try:
            summary = await self.service.get_cart_summary(user_id)
            return {
                "success": True,
                "message": "Cart summary retrieved successfully",
                "data": summary
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve cart summary: {str(e)}")

    async def add_to_cart(self, user_id: str, item: CartItemCreate) -> dict:
        """Add item to cart"""
        try:
            cart_item = await self.service.add_item_to_cart(user_id, item)
            return {
                "success": True,
                "message": "Item added to cart successfully",
                "data": cart_item
            }
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to add item to cart: {str(e)}")

    async def update_cart_item(self, user_id: str, item_id: int, quantity: int) -> dict:
        """Update quantity of a cart item"""
        try:
            if quantity < 0:
                raise HTTPException(status_code=400, detail="Quantity cannot be negative")

            updated_item = await self.service.update_cart_item(user_id, item_id, quantity)
            if not updated_item:
                raise HTTPException(status_code=404, detail="Cart item not found")

            return {
                "success": True,
                "message": "Cart item updated successfully",
                "data": updated_item
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update cart item: {str(e)}")

    async def remove_cart_item(self, user_id: str, item_id: int) -> dict:
        """Remove an item from cart"""
        try:
            success = await self.service.remove_cart_item(user_id, item_id)
            if not success:
                raise HTTPException(status_code=404, detail="Cart item not found")

            return {
                "success": True,
                "message": "Item removed from cart successfully"
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to remove cart item: {str(e)}")

    async def clear_cart(self, user_id: str) -> dict:
        """Remove all items from cart"""
        try:
            success = await self.service.clear_cart(user_id)
            return {
                "success": True,
                "message": "Cart cleared successfully"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to clear cart: {str(e)}")
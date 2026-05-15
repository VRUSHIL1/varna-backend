from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas import (
    Cart as CartSchema,
    CartItem as CartItemSchema,
    CartItemCreate,
    CartSummary
)
from app.services.cart_service import CartService

router = APIRouter(prefix="/api/cart", tags=["cart"])


@router.get("/{user_id}", response_model=CartSchema)
def get_cart(user_id: str, db: Session = Depends(get_db)):
    """Get cart for a user (creates if doesn't exist)"""
    try:
        service = CartService(db)
        cart = service.get_or_create_cart(user_id)
        return cart
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving cart: {str(e)}")


@router.get("/{user_id}/summary", response_model=CartSummary)
def get_cart_summary(user_id: str, db: Session = Depends(get_db)):
    """Get cart summary with total price and item count"""
    try:
        service = CartService(db)
        summary = service.get_cart_summary(user_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving cart summary: {str(e)}")


@router.post("/{user_id}/items", response_model=CartItemSchema, status_code=201)
def add_to_cart(
    user_id: str,
    item: CartItemCreate,
    db: Session = Depends(get_db)
):
    """Add item to cart"""
    try:
        service = CartService(db)
        cart_item = service.add_item_to_cart(user_id, item)
        return cart_item
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding item to cart: {str(e)}")


@router.put("/{user_id}/items/{item_id}", response_model=CartItemSchema)
def update_cart_item(
    user_id: str,
    item_id: int,
    item: CartItemCreate,
    db: Session = Depends(get_db)
):
    """Update quantity of a cart item"""
    try:
        service = CartService(db)
        updated_item = service.update_cart_item(user_id, item_id, item.quantity)
        if not updated_item:
            raise HTTPException(status_code=404, detail="Cart item not found")
        return updated_item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating cart item: {str(e)}")


@router.delete("/{user_id}/items/{item_id}")
def remove_cart_item(user_id: str, item_id: int, db: Session = Depends(get_db)):
    """Remove an item from cart"""
    try:
        service = CartService(db)
        success = service.remove_cart_item(user_id, item_id)
        if not success:
            raise HTTPException(status_code=404, detail="Cart item not found")
        return {"message": "Item removed from cart successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing cart item: {str(e)}")


@router.delete("/{user_id}")
def clear_cart(user_id: str, db: Session = Depends(get_db)):
    """Clear all items from cart"""
    try:
        service = CartService(db)
        success = service.clear_cart(user_id)
        return {"message": "Cart cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing cart: {str(e)}")
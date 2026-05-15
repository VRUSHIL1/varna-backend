from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.controllers.cart_controller import CartController
from app.schemas import CartItemCreate
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/cart", tags=["cart"])


@router.get("/me", response_model=dict)
async def get_cart(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Get cart for the current user"""
    controller = CartController(db)
    return await controller.get_cart(str(current_user.id))


@router.get("/me/summary", response_model=dict)
async def get_cart_summary(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Get cart summary with total price and item count"""
    controller = CartController(db)
    return await controller.get_cart_summary(str(current_user.id))


@router.post("/me/items", response_model=dict)
async def add_to_cart(
    item: CartItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Add item to cart"""
    controller = CartController(db)
    return await controller.add_to_cart(str(current_user.id), item)


@router.put("/me/items/{item_id}", response_model=dict)
async def update_cart_item(
    item_id: int,
    quantity: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Update quantity of a cart item"""
    controller = CartController(db)
    return await controller.update_cart_item(str(current_user.id), item_id, quantity)


@router.delete("/me/items/{item_id}", response_model=dict)
async def remove_cart_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Remove an item from cart"""
    controller = CartController(db)
    return await controller.remove_cart_item(str(current_user.id), item_id)


@router.delete("/me", response_model=dict)
async def clear_cart(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Remove all items from cart"""
    controller = CartController(db)
    return await controller.clear_cart(str(current_user.id))


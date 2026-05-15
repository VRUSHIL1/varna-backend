from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.controllers.order_controller import OrderController
from app.schemas import OrderCreate
from app.services.auth_service import get_current_user, get_current_admin

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("/", response_model=dict)
async def create_order(
    order: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Create a new order"""
    controller = OrderController(db)
    return await controller.create_order(order, str(current_user.id))


@router.get("/me", response_model=dict)
async def get_my_orders(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Get all orders for the current user"""
    controller = OrderController(db)
    return await controller.get_user_orders(str(current_user.id))


@router.get("/{order_id}", response_model=dict)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Get a specific order"""
    controller = OrderController(db)
    return await controller.get_order(order_id, current_user)


@router.put("/{order_id}/status", response_model=dict)
async def update_order_status(
    order_id: int,
    status: str,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    """Update order status"""
    controller = OrderController(db)
    return await controller.update_order_status(order_id, status)


@router.post("/{order_id}/cancel", response_model=dict)
async def cancel_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Cancel an order"""
    controller = OrderController(db)
    return await controller.cancel_order(order_id, current_user)


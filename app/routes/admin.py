from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.controllers.admin_controller import AdminController
from app.services.auth_service import get_current_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])


# User Management
@router.get("/users", response_model=dict)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: str = Query(None),
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    """List all users (admin only)"""
    controller = AdminController(db)
    return await controller.list_users(skip=skip, limit=limit, search=search)


@router.put("/users/{user_id}/role", response_model=dict)
async def update_user_role(
    user_id: int,
    role: str,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    """Update user role to admin or user (admin only)"""
    controller = AdminController(db)
    return await controller.update_user_role(user_id, role)


@router.put("/users/{user_id}/deactivate", response_model=dict)
async def deactivate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    """Deactivate a user (admin only)"""
    controller = AdminController(db)
    return await controller.deactivate_user(user_id)


@router.put("/users/{user_id}/activate", response_model=dict)
async def activate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    """Activate a user (admin only)"""
    controller = AdminController(db)
    return await controller.activate_user(user_id)


# Order Management
@router.get("/orders", response_model=dict)
async def list_all_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: str = Query(None),
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    """Get all orders across all users (admin only)"""
    controller = AdminController(db)
    return await controller.get_all_orders(skip=skip, limit=limit, status=status)


@router.get("/orders/{order_id}", response_model=dict)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    """Get a specific order (admin only)"""
    controller = AdminController(db)
    return await controller.get_order(order_id)


# Dashboard
@router.get("/stats", response_model=dict)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    """Get admin dashboard statistics (admin only)"""
    controller = AdminController(db)
    return await controller.get_stats()

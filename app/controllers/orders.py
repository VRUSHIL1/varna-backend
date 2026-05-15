from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import Order as OrderSchema, OrderCreate
from app.services.order_service import OrderService

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("/", response_model=OrderSchema, status_code=201)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """Create a new order from order items"""
    try:
        service = OrderService(db)
        new_order = service.create_order(order)
        return new_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating order: {str(e)}")


@router.get("/user/{user_id}", response_model=List[OrderSchema])
def get_user_orders(user_id: str, db: Session = Depends(get_db)):
    """Get all orders for a user"""
    try:
        service = OrderService(db)
        orders = service.get_user_orders(user_id)
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user orders: {str(e)}")


@router.get("/{order_id}", response_model=OrderSchema)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get a specific order"""
    try:
        service = OrderService(db)
        order = service.get_order_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving order: {str(e)}")


@router.put("/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    """Update order status (admin only in production)"""
    try:
        service = OrderService(db)
        updated_order = service.update_order_status(order_id, status)
        if not updated_order:
            raise HTTPException(status_code=404, detail="Order not found")
        return {
            "message": "Order status updated successfully",
            "order": updated_order
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating order status: {str(e)}")


@router.put("/{order_id}/cancel")
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    """Cancel an order and restore stock"""
    try:
        service = OrderService(db)
        cancelled_order = service.cancel_order(order_id)
        if not cancelled_order:
            raise HTTPException(status_code=404, detail="Order not found")
        return {
            "message": "Order cancelled successfully",
            "order": cancelled_order
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelling order: {str(e)}")
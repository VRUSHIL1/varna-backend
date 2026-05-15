from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import Optional, List
from app.models import Cart, CartItem, Product
from app.schemas import CartItemCreate, CartSummary


class CartService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_cart(self, user_id: str) -> Cart:
        """Get cart for user, create if doesn't exist"""
        query = select(Cart).where(Cart.user_id == user_id)
        result = await self.db.execute(query)
        cart = result.scalar_one_or_none()

        if not cart:
            cart = Cart(user_id=user_id)
            self.db.add(cart)
            await self.db.commit()
            await self.db.refresh(cart)

        return cart

    async def get_cart_summary(self, user_id: str) -> CartSummary:
        """Get cart summary with total price and item count"""
        cart = await self.get_or_create_cart(user_id)

        query = select(CartItem).where(CartItem.cart_id == cart.id)
        result = await self.db.execute(query)
        items = result.scalars().all()

        total_price = sum(item.product.price * item.quantity for item in items)
        total_items = sum(item.quantity for item in items)

        return CartSummary(
            total_items=total_items,
            total_price=total_price,
            items=items
        )

    async def add_item_to_cart(self, user_id: str, item_data: CartItemCreate) -> CartItem:
        """Add item to cart or update quantity if already exists"""
        cart = await self.get_or_create_cart(user_id)

        # Check product exists
        query = select(Product).where(Product.id == item_data.product_id)
        result = await self.db.execute(query)
        product = result.scalar_one_or_none()
        if not product:
            raise ValueError("Product not found")

        # Check if product already in cart
        query = select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == item_data.product_id
        )
        result = await self.db.execute(query)
        existing_item = result.scalar_one_or_none()

        if existing_item:
            # Update quantity
            existing_item.quantity += item_data.quantity
            self.db.add(existing_item)
            await self.db.commit()
            await self.db.refresh(existing_item)
            return existing_item
        else:
            # Add new item
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity
            )
            self.db.add(cart_item)
            await self.db.commit()
            await self.db.refresh(cart_item)
            return cart_item

    async def update_cart_item(self, user_id: str, item_id: int, quantity: int) -> Optional[CartItem]:
        """Update quantity of a cart item"""
        cart = await self.get_or_create_cart(user_id)

        query = select(CartItem).where(
            CartItem.id == item_id,
            CartItem.cart_id == cart.id
        )
        result = await self.db.execute(query)
        cart_item = result.scalar_one_or_none()

        if not cart_item:
            return None

        if quantity <= 0:
            # Remove item if quantity is 0 or negative
            self.db.delete(cart_item)
        else:
            cart_item.quantity = quantity
            self.db.add(cart_item)

        await self.db.commit()
        return cart_item if quantity > 0 else None

    async def remove_cart_item(self, user_id: str, item_id: int) -> bool:
        """Remove an item from cart"""
        cart = await self.get_or_create_cart(user_id)

        query = select(CartItem).where(
            CartItem.id == item_id,
            CartItem.cart_id == cart.id
        )
        result = await self.db.execute(query)
        cart_item = result.scalar_one_or_none()

        if not cart_item:
            return False

        self.db.delete(cart_item)
        await self.db.commit()
        return True

    async def clear_cart(self, user_id: str) -> bool:
        """Remove all items from cart"""
        cart = await self.get_or_create_cart(user_id)

        query = delete(CartItem).where(CartItem.cart_id == cart.id)
        await self.db.execute(query)
        await self.db.commit()
        return True
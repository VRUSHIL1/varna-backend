# Varna Backend API

A FastAPI backend for the Varna luxury saree collection e-commerce platform.

## Features

✅ **Product Catalog** - Browse sarees by category, search functionality
✅ **Shopping Cart** - Add/remove items, persistent cart per user
✅ **Orders** - Create orders, track status, inventory management
✅ **Database** - SQLite (easily upgrade to PostgreSQL)
✅ **API Documentation** - Auto-generated Swagger UI at `/api/docs`

## Quick Start

### 1. Setup Python Environment

```bash
cd e:\miraiminds\varna-backend
python -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Environment

```bash
copy .env.example .env
# Edit .env if needed (defaults are fine for development)
```

### 4. Run Server

```bash
python main.py
```

Server will start at: **http://localhost:8000**

### 5. Access API

- **API Docs (Swagger UI)**: http://localhost:8000/api/docs
- **API Health**: http://localhost:8000/api/health
- **Seed Sample Data**: http://localhost:8000/api/seed-data

## API Endpoints

### Products
- `GET /api/products` - List all products (with filtering, search, pagination)
- `GET /api/products/categories` - Get all categories
- `GET /api/products/{id}` - Get product details
- `POST /api/products` - Create product (admin)
- `PUT /api/products/{id}` - Update product (admin)
- `DELETE /api/products/{id}` - Delete product (admin)

### Shopping Cart
- `GET /api/cart/{user_id}` - Get user's cart
- `GET /api/cart/{user_id}/summary` - Get cart summary with totals
- `POST /api/cart/{user_id}/items` - Add item to cart
- `PUT /api/cart/{user_id}/items/{item_id}` - Update cart item quantity
- `DELETE /api/cart/{user_id}/items/{item_id}` - Remove item from cart
- `DELETE /api/cart/{user_id}` - Clear entire cart

### Orders
- `POST /api/orders` - Create new order
- `GET /api/orders/{order_id}` - Get order details
- `GET /api/orders/user/{user_id}` - Get user's orders
- `PUT /api/orders/{order_id}/status` - Update order status (admin)

## Frontend Integration

### CORS Setup
By default, CORS is enabled for:
- http://localhost:3000
- http://localhost:8000
- http://localhost:5173

Update `CORS_ORIGINS` in `.env` to add more origins.

### Example Frontend Calls

```javascript
// Get products
fetch('http://localhost:8000/api/products')
  .then(r => r.json())
  .then(products => console.log(products))

// Add to cart
fetch('http://localhost:8000/api/cart/user-123/items', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ product_id: 1, quantity: 2 })
})

// Create order
fetch('http://localhost:8000/api/orders', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: 'user-123',
    customer_name: 'John Doe',
    customer_email: 'john@example.com',
    customer_phone: '+91-9876543210',
    shipping_address: '123 Main St, City',
    items: [
      { product_id: 1, quantity: 1, price_at_purchase: 15000 }
    ]
  })
})
```

## Database

SQLite database file: `varna.db` (auto-created on startup)

### Models
- **Product** - Sarees with pricing, inventory, images
- **Cart** - User shopping carts
- **CartItem** - Items in cart with quantities
- **Order** - Customer orders with status tracking
- **OrderItem** - Line items in orders

## Development

### Add Sample Data
```bash
curl http://localhost:8000/api/seed-data
```

### View Database
Install SQLite browser or use Python:
```python
import sqlite3
conn = sqlite3.connect('varna.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM products")
print(cursor.fetchall())
```

## Next Steps

1. ✅ Connect frontend to these API endpoints
2. ⬜ Add user authentication (JWT)
3. ⬜ Add payment integration (Razorpay, Stripe)
4. ⬜ Add email notifications
5. ⬜ Add admin dashboard
6. ⬜ Deploy to cloud (Heroku, AWS, etc.)

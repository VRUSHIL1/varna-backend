from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from sqlalchemy import select

from app.database import init_db, AsyncSessionLocal
from app.routes import products, cart, orders, auth, admin
from app.models import Product, User, Order
from app.services.auth_service import AuthService

# Load environment variables
load_dotenv()

# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    await init_db()
    print("✓ Database initialized")
    yield
    # Shutdown (if needed)
    print("✓ Application shutting down")

app = FastAPI(
    title="Varna API",
    description="Backend API for Varna luxury saree collection",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# CORS configuration with default
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000,http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """API health check"""
    return {
        "status": "ok",
        "message": "Varna API is running",
        "docs": "/api/docs"
    }


@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Include route modules
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(auth.router)
app.include_router(admin.router)


@app.post("/api/seed-data")
async def seed_database():
    """Add sample products to database (development only)"""
    sample_products = [
        {
            "name": "Kanchipuram Silk Saree",
            "description": "Traditional gold-bordered Kanchipuram silk with intricate temple motifs",
            "price": 15000,
            "stock": 5,
            "sku": "KANCHI-001",
            "category": "Kanchipuram",
            "image_url": "/assets/saree-1.jpg",
            "color_url": "/assets/colors/saree-1-color.jpg",
            "displacement_url": "/assets/displacement/saree-1-disp.jpg"
        },
        {
            "name": "Benarasi Bridal Saree",
            "description": "Luxurious Benarasi saree with zari work and stone embellishments",
            "price": 25000,
            "stock": 3,
            "sku": "BENARASI-001",
            "category": "Benarasi",
            "image_url": "/assets/saree-2.jpg",
            "color_url": "/assets/colors/saree-2-color.jpg",
            "displacement_url": "/assets/displacement/saree-2-disp.jpg"
        },
        {
            "name": "Tussar Saree",
            "description": "Handwoven Tussar silk with tribal patterns",
            "price": 8500,
            "stock": 8,
            "sku": "TUSSAR-001",
            "category": "Tussar",
            "image_url": "/assets/saree-3.jpg",
            "color_url": "/assets/colors/saree-3-color.jpg",
            "displacement_url": "/assets/displacement/saree-3-disp.jpg"
        },
        {
            "name": "Chikhalwari Saree",
            "description": "Bengali saree with delicate embroidered borders",
            "price": 5500,
            "stock": 10,
            "sku": "CHIKHAL-001",
            "category": "Bengali",
            "image_url": "/assets/saree-4.jpg",
            "color_url": "/assets/colors/saree-4-color.jpg",
            "displacement_url": "/assets/displacement/saree-4-disp.jpg"
        },
    ]

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Product).limit(1))
        if result.scalar_one_or_none():
            return {"message": "Database already has products"}

        session.add_all([Product(**product) for product in sample_products])
        await session.commit()

    return {"success": True, "message": "Sample products seeded successfully"}


@app.post("/api/admin/create-first-admin")
async def create_first_admin(email: str, password: str, full_name: str = None):
    """Create the first admin user (development only). Fails if admin already exists."""
    async with AsyncSessionLocal() as session:
        auth_service = AuthService(session)
        
        if await auth_service.admin_exists():
            return {
                "success": False,
                "message": "Admin user already exists. Use admin login instead."
            }
        
        try:
            admin = await auth_service.create_admin_user(email, password, full_name)
            return {
                "success": True,
                "message": "Admin user created successfully",
                "data": {
                    "id": admin.id,
                    "email": admin.email,
                    "full_name": admin.full_name,
                    "role": admin.role
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to create admin: {str(e)}"
            }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

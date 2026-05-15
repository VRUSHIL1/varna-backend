from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from sqlalchemy import select

from app.database import init_db, AsyncSessionLocal
from app.routes import products, cart, orders, auth
from app.models import Product

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Varna API",
    description="Backend API for Varna luxury saree collection",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

# CORS configuration
cors_origins = os.getenv("CORS_ORIGINS").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()
    print("✓ Database initialized")


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

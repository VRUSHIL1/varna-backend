from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL from environment or default SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./varna.db")

# For SQLite, use StaticPool and check_same_thread=False for concurrent access
if DATABASE_URL.startswith("sqlite") or DATABASE_URL.startswith("sqlite+"):
    engine = create_async_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
else:
    engine = create_async_engine(DATABASE_URL, pool_pre_ping=True, echo=False)

AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)

# Base class for ORM models
class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """Dependency for FastAPI routes to get async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

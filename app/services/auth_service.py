import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.database import get_db
from app.models import User
from app.schemas import TokenData

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_google_id(self, google_id: str) -> Optional[User]:
        query = select(User).where(User.google_id == google_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_user(self, email: str, password: str, full_name: Optional[str] = None) -> User:
        hashed_password = get_password_hash(password)
        user = User(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            role="user",
            is_active=True,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def create_google_user(self, email: str, google_id: str, full_name: Optional[str] = None) -> User:
        user = User(
            email=email,
            full_name=full_name,
            google_id=google_id,
            role="user",
            is_active=True,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = await self.get_user_by_email(email)
        if not user or not user.hashed_password:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def verify_google_token(self, token: str) -> dict:
        if not GOOGLE_CLIENT_ID:
            raise ValueError("Google client ID is not configured")

        id_info = id_token.verify_oauth2_token(token, google_requests.Request(), GOOGLE_CLIENT_ID)
        if id_info["aud"] != GOOGLE_CLIENT_ID:
            raise ValueError("Google token audience mismatch")

        if not id_info.get("email_verified"):
            raise ValueError("Google email is not verified")

        return {
            "google_id": id_info["sub"],
            "email": id_info["email"],
            "full_name": id_info.get("name"),
        }

    async def create_or_get_google_user(self, google_id: str, email: str, full_name: Optional[str] = None) -> User:
        user = await self.get_user_by_google_id(google_id)
        if user:
            return user

        user = await self.get_user_by_email(email)
        if user:
            user.google_id = google_id
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user

        return await self.create_google_user(email, google_id=google_id, full_name=full_name)

    async def admin_exists(self) -> bool:
        """Check if any admin user exists"""
        query = select(User).where(User.role == "admin")
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def create_admin_user(self, email: str, password: str, full_name: Optional[str] = None) -> User:
        """Create a new admin user"""
        hashed_password = get_password_hash(password)
        user = User(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            role="admin",
            is_active=True,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def promote_to_admin(self, user_id: int) -> Optional[User]:
        """Promote a user to admin role"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        user.role = "admin"
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def demote_from_admin(self, user_id: int) -> Optional[User]:
        """Demote an admin user to regular user"""
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        user.role = "user"
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(sub=user_id, email=payload.get("email"), role=payload.get("role"))
    except JWTError:
        raise credentials_exception

    service = AuthService(db)
    user = await service.get_user_by_id(int(token_data.sub))
    if user is None:
        raise credentials_exception
    return user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

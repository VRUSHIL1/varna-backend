from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth_service import AuthService, create_access_token
from app.schemas import UserCreate


class AuthController:
    def __init__(self, db: AsyncSession):
        self.service = AuthService(db)

    async def signup(self, user_data: UserCreate) -> dict:
        existing = await self.service.get_user_by_email(user_data.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        user = await self.service.create_user(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
        )
        token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role})
        return {
            "success": True,
            "message": "User registered successfully",
            "data": {
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "google_id": user.google_id,
                    "is_active": user.is_active,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at,
                },
            },
        }

    async def login(self, username: str, password: str) -> dict:
        user = await self.service.authenticate_user(username, password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role})
        return {
            "success": True,
            "message": "Login successful",
            "data": {
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "google_id": user.google_id,
                    "is_active": user.is_active,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at,
                },
            },
        }

    async def google_login(self, id_token: str) -> dict:
        google_info = await self.service.verify_google_token(id_token)
        user = await self.service.create_or_get_google_user(
            google_id=google_info["google_id"],
            email=google_info["email"],
            full_name=google_info.get("full_name"),
        )

        token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role})
        return {
            "success": True,
            "message": "Google login successful",
            "data": {
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "google_id": user.google_id,
                    "is_active": user.is_active,
                    "created_at": user.created_at,
                    "updated_at": user.updated_at,
                },
            },
        }

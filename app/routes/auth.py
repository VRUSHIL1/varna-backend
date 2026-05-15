from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.controllers.auth_controller import AuthController
from app.schemas import UserCreate, GoogleLogin

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/signup", response_model=dict)
async def signup(user: UserCreate, db: AsyncSession = Depends(get_db)):
    controller = AuthController(db)
    return await controller.signup(user)


@router.post("/login", response_model=dict)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    controller = AuthController(db)
    return await controller.login(form_data.username, form_data.password)


@router.post("/google", response_model=dict)
async def google_login(payload: GoogleLogin, db: AsyncSession = Depends(get_db)):
    controller = AuthController(db)
    return await controller.google_login(payload.id_token)

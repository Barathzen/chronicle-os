from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import UserCreate, UserOut, Token
from app.db.database import get_db
from app.services.auth.service import (
    create_user,
    authenticate_user,
    create_token_for_user,
    get_user_by_email,
)

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    exists = await get_user_by_email(db, user_in.email)
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await create_user(db, user_in.email, user_in.password)
    return user


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.email, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = create_token_for_user(user)
    return {"access_token": access_token, "token_type": "bearer"}

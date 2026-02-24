"""
Authentication routes.
MODIFIED: Simplified for no-auth mode. 
Only keeps register/login for compatibility/updating the default user if desired, 
but they accept any credentials.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from src.config.database import get_db
from src.models.user_models import User
from src.api.schemas import UserRegister, Token
from src.api.auth import get_current_active_user

router = APIRouter()

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Mock registration. 
    In no-auth mode, this just returns a dummy token.
    You can still use this to update the guest user properties if we wanted to expand logic,
    but for now it just returns success.
    """
    return {"access_token": "dummy-token", "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Mock login.
    Always returns success.
    """
    return {"access_token": "dummy-token", "token_type": "bearer"}

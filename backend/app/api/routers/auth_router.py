from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import LoginRequest, RegisterRequest, LoginResponse, RegisterResponse, RefreshTokenRequest
from app.core.security import refresh_access_token

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/register", response_model=RegisterResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    try:
        auth_service = AuthService(db)
        user = auth_service.register_user(request.username, request.email, request.password)
        return RegisterResponse(message="User registered successfully", user_id=user.id, username=user.username)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=LoginResponse)
def login(formdata: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        auth_service = AuthService(db)
        token = auth_service.login_user(formdata.username, formdata.password)
        return token
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/refresh", response_model=LoginResponse)
def refresh(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        auth_service = AuthService(db)
        new_tokens = auth_service.refresh_access_token(request.refresh_token)
        return new_tokens
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

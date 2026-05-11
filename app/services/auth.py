from sqlalchemy.orm import Session

from app.models.user import User

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token
)

def register_user(db: Session, username: str, email: str, password: str) -> User:
    
    existig_user = db.query(User).filter(User.username == username).first()
    if existig_user:
        raise ValueError("Username already registered")
    
    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def login_user(db: Session, username: str, password: str) -> dict:
    user = authenticate_user(db, username, password)
    if not user:
        raise ValueError("Invalid username or password")
    
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token(data={"sub": str(user.id), "role": user.role})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }



from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.services.user_service import UserService
from app.schemas.user import UserResponse, UserCreateRequest, UserUpdateRequest
from app.core.deps import get_current_user, require_admin
from app.db.base import get_db

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

# @router.post("/", response_model=UserResponse)
# def create_user(user: UserCreateRequest, db: Session = Depends(get_db)):
#     user_service = UserService(db)
#     return user_service.create_user(user)

@router.get("/", response_model=list[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), admin=Depends(require_admin)):
    user_service = UserService(db)
    return user_service.get_users(skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    user_service = UserService(db)
    db_user = user_service.get_user(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdateRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user["user_id"] != user_id and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not allowed to update other users")
    
    user_service = UserService(db)
    db_user = user_service.update_user(user_id, user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    user_service = UserService(db)
    success = user_service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

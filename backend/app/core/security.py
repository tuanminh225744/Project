from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi.security import HTTPBearer
from fastapi import HTTPException
import os

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    toEncode = data.copy()
    
    expire = datetime.utcnow() + timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15")))
    toEncode.update({"exp": expire})
    return jwt.encode(toEncode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM", "HS256"))

def create_refresh_token(data: dict) -> str:
    toEncode = data.copy()
    
    expire = datetime.utcnow() + timedelta(days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")))
    toEncode.update({"exp": expire})
    return jwt.encode(toEncode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM", "HS256"))

def decode_access_token(token: str) -> dict:
    try:
        
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM", "HS256")])
    
        return payload
    except jwt.JWTError as e:
        print(f"[decode_access_token] JWTError: {e}")
        return None

def decode_refresh_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM", "HS256")])
        return payload
    except jwt.JWTError:
        return None
    
def refresh_access_token(token: str) -> dict:
    payload = decode_refresh_token(token)
    if not payload:
        raise ValueError("Invalid refresh token")
    
    user_id = payload.get("sub")

    if user_id is None:
        raise ValueError("Invalid refresh token")

    new_access_token = create_access_token(data={"sub": user_id})
    new_refresh_token = create_refresh_token(data={"sub": user_id})
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM", "HS256")])
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(401, "Invalid refresh token")

        return {
            "user_id": int(user_id),
        }

    except (JWTError, ValueError) as e:
        print(f"JWT/Parse Error: {e}")
        raise HTTPException(401, "Invalid refresh token")
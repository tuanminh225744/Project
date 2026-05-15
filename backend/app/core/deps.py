from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from dotenv import load_dotenv
import os
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

load_dotenv()

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM", "HS256")])
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(401, "Invalid token")

        return {
            "user_id": int(user_id),
        }

    except (JWTError, ValueError) as e:
        print(f"JWT/Parse Error: {e}")
        raise HTTPException(401, "Invalid token")

# def require_admin(current_user=Depends(get_current_user)):
#     if current_user["role"] != "admin":
#         raise HTTPException(
#             status_code=403,
#             detail="Admin only"
#         )
#     return current_user
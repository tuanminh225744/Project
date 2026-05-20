from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from dotenv import load_dotenv
import os
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

load_dotenv()

def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Bạn cần đăng nhập để thực hiện thao tác này.")

    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM", "HS256")])
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token không hợp lệ.")

        return {
            "user_id": int(user_id),
        }

    except (JWTError, ValueError) as e:
        print(f"JWT/Parse Error: {e}")
        raise HTTPException(status_code=401, detail="Token không hợp lệ.")

# def require_admin(current_user=Depends(get_current_user)):
#     if current_user["role"] != "admin":
#         raise HTTPException(
#             status_code=403,
#             detail="Admin only"
#         )
#     return current_user

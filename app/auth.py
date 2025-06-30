from passlib.context import CryptContext
from fastapi import HTTPException
from jose import jwt,JWTError
from datetime import datetime,timedelta
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

def hash_password(Password: str):
    try:
        return pwd_context.hash(Password)
    except Exception as e:
        raise HTTPException(status_code=404,detail=f"Hashing failed: {str(e)}")

def verify_password(Password: str,hashed: str):
    try:
        return pwd_context.verify(Password,hashed)
    except Exception as e:
        raise HTTPException(status_code=404,detail=f"Password verification failed: {str(e)}")
    
def create_access_token(data:dict):
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    except JWTError as e:
        raise HTTPException(status_code=404,detail=f"Token generation failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"Internal error: {str(e)}")
    
def decode(token: str):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
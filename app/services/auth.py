"""
Authentication service for AgriSmart
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

from ..models.schemas import UserCreate, UserResponse
from ..database import DatabaseManager

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Database instance
db = DatabaseManager()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any]) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def create_user(user_data: UserCreate) -> UserResponse:
    """Create a new user"""
    # Check if user exists
    existing_user = await db.get_user_by_email(user_data.email)
    if existing_user:
        raise ValueError("Email already registered")
    
    # Create user with hashed password
    hashed_password = get_password_hash(user_data.password)
    db_user = await db.create_user({
        "email": user_data.email,
        "full_name": user_data.full_name,
        "password_hash": hashed_password
    })
    
    if not db_user:
        raise ValueError("Failed to create user")
    
    return UserResponse(**db_user)

async def authenticate_user(email: str, password: str) -> Optional[UserResponse]:
    """Authenticate user with email and password"""
    user = await db.get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return UserResponse(**user)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserResponse:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = await db.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
        
    return UserResponse(**user)
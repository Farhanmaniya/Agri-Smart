"""
Simple Authentication API for AgriSmart demo with Supabase
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
import hashlib
import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

router = APIRouter()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

# Initialize Supabase client
supabase: Client = None
try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase client initialized successfully")
    else:
        print("⚠️ Supabase credentials not found, using mock database")
except Exception as e:
    print(f"⚠️ Failed to initialize Supabase: {e}, using mock database")

# Mock user database (in production, this would be Supabase)
MOCK_USERS = {
    "farmer@agrismart.com": {
        "id": "1",
        "email": "farmer@agrismart.com",
        "full_name": "Farm Manager",
        "password_hash": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",  # "password"
        "created_at": "2025-01-01T00:00:00Z"
    },
    "demo@agrismart.com": {
        "id": "2", 
        "email": "demo@agrismart.com",
        "full_name": "Demo User",
        "password_hash": "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f",  # "demo123"
        "created_at": "2025-01-01T00:00:00Z"
    }
}

SECRET_KEY = "your-secret-key-here"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    created_at: str

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login", response_model=TokenResponse)
async def login(user_credentials: UserLogin):
    """Authenticate user and return access token"""
    
    # Check if user exists
    user = MOCK_USERS.get(user_credentials.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(user_credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "user_id": user["id"]},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        user={
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"]
        }
    )

@router.post("/register")
async def register_user(user_data: UserRegister):
    """Register a new user with Supabase integration."""
    try:
        # Try Supabase first
        if supabase:
            try:
                # Check if user exists in Supabase
                existing_user = supabase.table('users').select('*').eq('email', user_data.email).execute()
                if existing_user.data:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="User already exists"
                    )
                
                # Hash password
                password_hash = hashlib.sha256(user_data.password.encode()).hexdigest()
                
                # Insert user into Supabase
                new_user_data = {
                    "email": user_data.email,
                    "full_name": user_data.full_name,
                    "password_hash": password_hash,
                    "created_at": datetime.utcnow().isoformat()
                }
                
                result = supabase.table('users').insert(new_user_data).execute()
                
                if result.data:
                    user_record = result.data[0]
                    
                    # Generate JWT token
                    token_data = {
                        "sub": user_record["email"],
                        "user_id": str(user_record["id"]),
                        "full_name": user_record["full_name"],
                        "exp": datetime.utcnow() + timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
                    }
                    
                    token = jwt.encode(token_data, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM", "HS256"))
                    
                    return {
                        "access_token": token,
                        "token_type": "bearer",
                        "user": {
                            "id": str(user_record["id"]),
                            "email": user_record["email"],
                            "full_name": user_record["full_name"]
                        },
                        "message": "User registered successfully in Supabase"
                    }
                    
            except Exception as supabase_error:
                print(f"Supabase registration failed: {supabase_error}")
                # Fall back to mock database
        
        # Fallback to mock database
        if user_data.email in MOCK_USERS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )
        
        # Hash password
        password_hash = hashlib.sha256(user_data.password.encode()).hexdigest()
        
        # Create new user
        new_user = {
            "id": str(len(MOCK_USERS) + 1),
            "email": user_data.email,
            "full_name": user_data.full_name,
            "password_hash": password_hash,
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        
        # Add to mock database
        MOCK_USERS[user_data.email] = new_user
        
        # Generate JWT token
        token_data = {
            "sub": new_user["email"],
            "user_id": new_user["id"],
            "full_name": new_user["full_name"],
            "exp": datetime.utcnow() + timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
        }
        
        token = jwt.encode(token_data, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM", "HS256"))
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": new_user["id"],
                "email": new_user["email"],
                "full_name": new_user["full_name"]
            },
            "message": "User registered successfully (mock database)"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(token: str):
    """Get current user information from token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = MOCK_USERS.get(email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        created_at=user["created_at"]
    )

@router.get("/")
async def auth_info():
    """Get authentication API information"""
    return {
        "message": "AgriSmart Authentication API",
        "endpoints": [
            "POST /login - Authenticate user",
            "POST /register - Register new user", 
            "GET /me - Get current user info"
        ],
        "demo_accounts": [
            {"email": "farmer@agrismart.com", "password": "password"},
            {"email": "demo@agrismart.com", "password": "demo123"}
        ]
    }

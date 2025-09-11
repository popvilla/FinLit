import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from .database import supabase
from .models import TokenData, UserInDB

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable not set.")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashes a plain password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a JWT access token.

    Args:
        data (dict): The data to encode into the token (e.g., {"sub": user_id, "role": user_role}).
        expires_delta (Optional[timedelta]): The timedelta for token expiration.
                                             If None, uses ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """
    Retrieves the current user based on the provided JWT token.

    Raises:
        HTTPException: If credentials cannot be validated or user not found.

    Returns:
        UserInDB: The authenticated user's data.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        token_data = TokenData(id=UUID(user_id_str))
    except JWTError:
        raise credentials_exception

    # Fetch user from Supabase (assuming 'id' in users table matches 'sub' in JWT)
    response = supabase.table("users").select("*").eq("id", token_data.id).single().execute()
    user_data = response.data

    if user_data is None:
        raise credentials_exception
    return UserInDB(**user_data)

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """
    Dependency to get the current active user.
    Additional checks for user activity status can be added here if needed.
    """
    return current_user

async def get_current_admin_user(current_user: UserInDB = Depends(get_current_active_user)) -> UserInDB:
    """
    Dependency to get the current user, ensuring they have 'admin' role.
    """
    if current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return current_user

async def get_current_instructor_user(current_user: UserInDB = Depends(get_current_active_user)) -> UserInDB:
    """
    Dependency to get the current user, ensuring they have 'instructor' or 'admin' role.
    """
    if current_user.role not in ['instructor', 'admin']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return current_user

async def get_current_student_user(current_user: UserInDB = Depends(get_current_active_user)) -> UserInDB:
    """
    Dependency to get the current user, ensuring they have 'student', 'instructor', or 'admin' role.
    This allows instructors and admins to also access student-level functionalities.
    """
    if current_user.role not in ['student', 'instructor', 'admin']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return current_user
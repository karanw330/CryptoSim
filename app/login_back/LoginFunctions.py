from app.db_init import get_db_connection
import os
import jwt
import random
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from dotenv import load_dotenv
from .LoginPydanticModels import *

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = os.getenv("HASHING_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    test = password_hash.hash(password)
    print(test)
    return test


def get_user(username: str | None = None, email: str | None = None, sub: str | None = None):
    conn = get_db_connection()
    user_row = conn.execute('SELECT * FROM users WHERE username = ? OR email = ? OR sub = ?', (username,email,sub)).fetchone()
    conn.close()
    
    if user_row:
        return UserInDB(**dict(user_row))
    return None


def create_user(user_data: UserCreate):
    conn = get_db_connection()
    try:
        # Check if username or email already exists
        existing_user = conn.execute(
            'SELECT * FROM users WHERE username = ? OR email = ? OR sub = ?',
            (user_data.username, user_data.email, user_data.sub)
        ).fetchone()
        
        if existing_user:
            return {"error": "Username or email already exists"}
        
        hashed_pwd = get_password_hash(user_data.password)
        conn.execute(
            'INSERT INTO users (username, email, sub, hashed_password, disabled, balance_usd) VALUES (?, ?, ?, ?, ?, ?)',
            (user_data.username, user_data.email, user_data.sub, hashed_pwd, 0, 100000.0)
        )
        conn.commit()
        
        # Return the created user (as UserInDB)
        return get_user(user_data.username, user_data.email, user_data.sub)
    except Exception as e:
        print(f"Error creating user: {e}")
        return {"error": "Failed to create user"}
    finally:
        conn.close()


def authenticate_user(username: str, password: str):
    user = get_user(username= username)
    if not user:
        return {"error": {"type":"user", "content":"User not found"}}
    if not verify_password(password, user.hashed_password):
        return {"error": {"type":"password", "content":"Incorrect password"}}
    return user

def authenticate_google_user(sub: str):
    user = get_user(sub=sub)
    if not user:
        return {"error": {"type":"user", "content":"User not found"}}
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# OTP In-memory store: {email: {"otp": str, "expires": datetime}}
otp_store = {}

def generate_otp(email: str):
    otp = str(random.randint(100000, 999999))
    expires = datetime.now(timezone.utc) + timedelta(minutes=5)
    otp_store[email] = {"otp": otp, "expires": expires}
    print(f"DEBUG: OTP for {email} is {otp}")
    return otp

def verify_otp_logic(email: str, otp: str):
    if email not in otp_store:
        return False
    
    stored_data = otp_store[email]
    if datetime.now(timezone.utc) > stored_data["expires"]:
        del otp_store[email]
        return False
    
    if stored_data["otp"] == otp:
        # Check if user exists (necessary for generating token)
        user = get_user(email=email)
        if user:
            # Clear OTP after successful verification
            del otp_store[email]
            return user
        
    return False

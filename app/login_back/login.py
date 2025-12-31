from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import timedelta
from typing import Annotated
from .LoginPydanticModels import *
from .LoginFunctions import *
from pwdlib import PasswordHash
from jwt.exceptions import InvalidTokenError

Router = APIRouter()

@Router.post("/token", response_model=Token)
async def login_for_access_token(data : LoginRequest):
    if (data.sub is not None) and (data.sub != ""):
        user = authenticate_google_user(data.sub)
        print("user authenticated via google:", user)
    else:
        user = authenticate_user(data.email, data.password)
        print("user authenticated via email:", user)
    if "error" in user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=user["error"],
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(user.username)
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "refresh_token": refresh_token
    }


@Router.post("/register", response_model=Token)
async def register_user(user_data: UserCreate):
    user = create_user(user_data)
    if "error" in user:
        print(user)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=user["error"],
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(user.username)
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "refresh_token": refresh_token
    }


@Router.post("/send-otp")
async def send_otp_route(data: OTPRequest):
    user = get_user(email=data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not registered"
        )
    
    generate_otp(data.email)
    return {"message": "OTP sent successfully"}


@Router.post("/verify-otp", response_model=Token)
async def verify_otp_route(data: OTPVerify):
    user = verify_otp_logic(data.email, data.otp)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(user.username)
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "refresh_token": refresh_token
    }

@Router.post("/refresh", response_model=Token)
async def refresh_token_route(data: RefreshTokenRequest):
    username = verify_refresh_token(data.refresh_token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    # We can either return the same refresh token or a new one. 
    # For simplicity, returning the same one.
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "refresh_token": data.refresh_token
    }

@Router.post("/reset-password")
async def reset_password_route(data: PasswordResetRequest):
    # This assumes OTP was already verified and email is valid
    success = reset_password(data.email, data.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to reset password"
        )
    return {"message": "Password reset successfully"}


@Router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@Router.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    from app.db_init import get_db_connection
    conn = get_db_connection()
    items = conn.execute('SELECT symbol, amount FROM portfolio WHERE user_id = ?', 
                        (current_user.username,)).fetchall()
    
    # Also fetch active orders to show "reserved" amounts or just list them if needed
    # For now, just return portfolio holdings plus dummy "owner" field to match existing pattern if any
    
    # Existing code returned: [{"item_id": "Foo", "owner": current_user.username}]
    # We will return list of holdings
    
    result = []
    for item in items:
        result.append({
            "item_id": item['symbol'], 
            "amount": item['amount'],
            "owner": current_user.username
        })
        
    conn.close()
    return result

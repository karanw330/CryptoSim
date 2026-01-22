from fastapi import APIRouter, HTTPException, status, Depends
from .OtpPydanticModels import OTPRequest, OTPVerify
from app.login_back.LoginPydanticModels import Token
from app.login_back.LoginFunctions import (
    otp_store, get_user, verify_otp_logic, 
    create_access_token, create_refresh_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from .otp_function import generate_otp, send_otp_email
from datetime import datetime, timedelta, timezone

router = APIRouter()

@router.post("/send_otp")
async def send_otp(data: OTPRequest):
    user = get_user(email=data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not registered"
        )
    
    otp = generate_otp()
    expires = datetime.now(timezone.utc) + timedelta(minutes=5)
    otp_store[data.email] = {"otp": str(otp), "expires": expires}
    
    print(f"DEBUG: Sending OTP {otp} to {data.email}")
    success = send_otp_email(data.email, otp)
    if not success:
        # Fallback to console log for development if email fails
        print(f"ERROR: Failed to send email to {data.email}. OTP is {otp}")
        # We still return 200 for now to allow development flow if needed, 
        # or raise 500. Let's raise 500 for strictness.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP email. Please check server logs."
        )
    
    return {"message": "OTP sent successfully"}

@router.post("/verify_otp", response_model=Token)
async def verify_otp_route(data: OTPVerify):
    """Verifies the OTP and returns a session token."""
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
from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str | None = None
    sub : str | None = None

class UserCreate(BaseModel):
    username: str
    email: str
    password: str | None = None
    sub: str | None = None

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    sub: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str | None = None
    sub: str | None = None

class OTPRequest(BaseModel):
    email: str

class OTPVerify(BaseModel):
    email: str
    otp: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class PasswordResetRequest(BaseModel):
    email: str
    new_password: str
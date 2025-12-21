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
    # form_data will be an instance of OAuth2PasswordRequestForm provided by FastAPI
    user = authenticate_user(data.email, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token":access_token, "token_type":"bearer"}


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

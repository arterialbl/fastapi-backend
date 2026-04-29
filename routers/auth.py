from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
from sqlalchemy.orm import Session

from database import get_db
from schemas import User, UserUpdate, PasswordChange, RefreshTokenRequest, LogoutRequest
from models import UserDB, RevokedTokenDB
from crud import login_user, update_current_user, change_current_password, delete_current_user, logout_user
from auth import decode_access_token, create_access_token

router = APIRouter(tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
    )

    try:
        payload = decode_access_token(token)
        email = payload.get("sub")

        if email is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = db.query(UserDB).filter(UserDB.email == email).first()

    if user is None:
        raise credentials_exception

    return user

def get_current_admin(current_user: UserDB = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user

def user_active(current_user: UserDB = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Disactivated")
    return current_user

@router.post("/login")
def login_route(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    return login_user(form_data, db)

@router.post("/logout")
def logout_route(
    token_data: LogoutRequest,
    db: Session = Depends(get_db),
):
    return logout_user(token_data.refresh_token, db)

@router.post("/refresh")
def refresh_token_route(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
): 
    revoked_token = db.query(RevokedTokenDB).filter(
    RevokedTokenDB.token == token_data.refresh_token
    ).first()

    if revoked_token:
        raise HTTPException(
            status_code=401,
            detail="Refresh token has been revoked",
        )
    
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
    )

    try:
        payload = decode_access_token(token_data.refresh_token)

        if payload.get("type") != "refresh":
            raise credentials_exception

        email = payload.get("sub")

        if email is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    access_token = create_access_token({"sub": email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.get("/me", response_model=User)
def read_current_user(current_user: UserDB = Depends(get_current_user)):
    return current_user


@router.patch("/me/password")
def change_my_password(
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    return change_current_password(current_user, password_data, db)


@router.patch("/me", response_model=User)
def update_me_route(
    updated_user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    return update_current_user(current_user, updated_user, db)


@router.delete("/me")
def delete_me_route(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    return delete_current_user(current_user, db)
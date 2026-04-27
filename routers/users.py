from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas import User, UserCreate, UserUpdate, UsersListResponse
from models import UserDB
from crud import get_users, get_user, create_user, update_user, delete_user, deactivate_user, activate_user
from routers.auth import get_current_user, get_current_admin

router = APIRouter(tags=["Users"])


@router.get("/users", response_model=UsersListResponse)
def get_users_route(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_admin),
    is_active: bool | None = Query(default=None, description="Filter by active status"),
    is_admin: bool | None = Query(default=None, description="Filter by admin status"),
    search: str | None = Query(default=None, description="Search by name or email"),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return get_users(db, is_active, is_admin, search, limit, offset)

@router.get("/users/{user_id}", response_model=User)
def get_user_route(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    return get_user(user_id, db)


@router.post("/users", status_code=201, response_model=User)
def create_user_route(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    return create_user(user, db)


@router.patch("/users/{user_id}", response_model=User)
def update_user_route(
    user_id: int,
    updated_user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_admin),
):
    return update_user(user_id, updated_user, db)

@router.patch("/users/{user_id}/deactivate", response_model=User)
def deactivate_user_route(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_admin),
):
    return deactivate_user(user_id, db)


@router.patch("/users/{user_id}/activate", response_model=User)
def activate_user_route(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_admin),
):
    return activate_user(user_id, db)

@router.delete("/users/{user_id}", response_model=User)
def delete_user_route(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_admin),
):
    return delete_user(user_id, db)
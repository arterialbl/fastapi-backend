from models import UserDB
from sqlalchemy.orm import Session
from fastapi import HTTPException
from security import hash_password, verify_password
from auth import create_access_token

def get_users(
    db: Session,
    is_active: bool | None = None,
    is_admin: bool | None = None,
    search: str | None = None,
    limit: int = 10,
    offset: int = 0,
):
    query = db.query(UserDB)

    if is_active is not None:
        query = query.filter(UserDB.is_active == is_active)

    if is_admin is not None:
        query = query.filter(UserDB.is_admin == is_admin)

    if search is not None:
        query = query.filter(
            (UserDB.name.ilike(f"%{search}%")) |
            (UserDB.email.ilike(f"%{search}%"))
        )

    total = query.count()
    items = query.offset(offset).limit(limit).all()

    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
    }

def get_user_or_404(user_id: int, db: Session):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

def check_email_unique(email: str, db: Session, exclude_user_id: int | None = None):
    existing_user = db.query(UserDB).filter(UserDB.email == email).first()

    if existing_user and (exclude_user_id is None or existing_user.id != exclude_user_id):
        raise HTTPException(status_code=400, detail="Email already exists")

def update_current_password(current_user, password_data, db: Session):
    current_user.password_hash = hash_password(password_data.password)
    db.commit()
    db.refresh(current_user)
    return {"message": "Password updated successfully"}

def login_user(form_data, db: Session):
    user = db.query(UserDB).filter(UserDB.email == form_data.username).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")

    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token({"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}

def get_user(user_id: int, db: Session):
    return get_user_or_404(user_id, db)


def create_user(user, db: Session):
    if user.email is not None:
        check_email_unique(user.email, db)
    new_user = UserDB(name=user.name, email=user.email, password_hash=hash_password(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

def delete_user(user_id: int, db: Session):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return user

def update_user(user_id: int, updated_user, db: Session):
    user = get_user_or_404(user_id, db)
    
    if updated_user.name is not None:
        user.name = updated_user.name

    if updated_user.email is not None:
        check_email_unique(updated_user.email, db, exclude_user_id=user_id)
        user.email = updated_user.email
    
    if updated_user.is_active is not None:
        user.is_active = updated_user.is_active


    db.commit()
    db.refresh(user)

    return user

def deactivate_user(user_id: int, db: Session):
    user = get_user_or_404(user_id, db)
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


def activate_user(user_id: int, db: Session):
    user = get_user_or_404(user_id, db)
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user


def update_current_user(current_user, updated_user, db: Session):
    if updated_user.name is not None:
        current_user.name = updated_user.name

    if updated_user.email is not None:
        check_email_unique(updated_user.email, db, exclude_user_id=current_user.id)
        current_user.email = updated_user.email

    db.commit()
    db.refresh(current_user)

    return current_user

def change_current_password(current_user, password_data, db: Session):
    if not verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid current password")

    current_user.password_hash = hash_password(password_data.new_password)
    db.commit()
    db.refresh(current_user)

    return {"message": "Password changed successfully"}

def delete_current_user(current_user, db: Session):
    db.delete(current_user)
    db.commit()
    return {"message": "User deleted successfully"}
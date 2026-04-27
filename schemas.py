from pydantic import BaseModel, Field, EmailStr

class User(BaseModel):
    id: int
    name: str = Field(min_length=2, max_length=50)
    email: EmailStr | None = None
    is_admin: bool

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    email: EmailStr | None = None
    password: str = Field(min_length=6, max_length=128)

class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=50)
    email: EmailStr | None = None
    is_active: bool | None = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)

class PasswordUpdate(BaseModel):
    password: str = Field(min_length=6, max_length=128)

class PasswordChange(BaseModel):
    old_password: str = Field(min_length=6, max_length=128)
    new_password: str = Field(min_length=6, max_length=128)

class UsersListResponse(BaseModel):
    items: list[User]
    total: int
    limit: int
    offset: int


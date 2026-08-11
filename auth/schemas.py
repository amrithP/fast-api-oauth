from pydantic import BaseModel,EmailStr
from typing import Optional

#Schema for user creation
class UserCreate(BaseModel):
    username:str
    email:EmailStr
    password:str
    role:str

#Schema for user login 
class UserLogin(BaseModel):
    username:str
    password:str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

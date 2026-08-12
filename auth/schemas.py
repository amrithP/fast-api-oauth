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

class RoleCreate(BaseModel):
    #id not req as its auto incremented
    name: str

#RoleOut defines the shape of the response, and from_attributes = True is what allows FastAPI to build that response directly from a database object's attributes instead of requiring you to convert it to a dict by hand first.
class RoleOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True         #new_role is not a dict , its a sqlalchemy object .So to read and rreeturn as ouput , we have set from_attributes=true


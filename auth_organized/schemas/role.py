from pydantic import BaseModel


class RoleCreate(BaseModel):
    # id not required, it's auto-incremented
    name: str


class RoleOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True  # lets FastAPI build the response straight from the SQLAlchemy object

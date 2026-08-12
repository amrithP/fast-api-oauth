from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from auth_organized.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100))
    hashed_password = Column(String(255))

    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    role = relationship("Role", back_populates="users")  # user.role.name to read the role name

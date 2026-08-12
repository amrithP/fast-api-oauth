from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from auth_database import Base

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name = Column(String(50), unique=True, nullable=False)

    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100))
    hashed_password = Column(String(255))

    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    role = relationship("Role", back_populates="users")   #user.role.name   to access the roles table ,use role


#what to change and what not to change after foreign key 
"""What does NOT need to change
get_current_user, require_roles, /protected, /user/dashboard, /admin/dashboard, /profile, change_password — all of these only ever read current_user["role"], which comes from the JWT payload, not the database. Since your token still stores role as a plain string name (user.role.name at login time), these all keep working unchanged.
PasswordChange, UserUpdate schemas — no changes needed (role stays Optional[str] there, since the client still types the role name, not an ID).


Quick checklist to apply in order
schemas.py: remove id from RoleCreate
create_role: remove id=payload.id
/signup: role = user.role → role_id = role_exists.id, and fix the return line
/login: "role":user.role → "role":user.role.name
update_user: add role lookup, user.role_id = role.id, fix return line
delete_role: User.role == role.name → User.role_id == role.id
Go through these one at a time, and re-test each endpoint in Swagger after each change so you can tell exactly which one breaks if something goes wrong.

"""
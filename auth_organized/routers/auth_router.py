from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth_organized.core.config import VALID_CLIENT_ID, VALID_CLIENT_SECRET
from auth_organized.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    require_roles,
    verify_password,
)
from auth_organized.db.database import get_db
from auth_organized.models import Role, User
from auth_organized.schemas.role import RoleCreate, RoleOut
from auth_organized.schemas.user import PasswordChange, UserCreate, UserUpdate

router = APIRouter()


@router.post("/signup")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exits")

    role_exists = db.query(Role).filter(Role.name == user.role).first()
    if not role_exists:
        raise HTTPException(status_code=400, detail="Invalid role")

    hashed_password = hash_password(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role_id=role_exists.id,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role.name,
    }


@router.post("/login")
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    if form_data.client_id != VALID_CLIENT_ID or form_data.client_secret != VALID_CLIENT_SECRET:
        raise HTTPException(status_code=401, detail="Invalid client credentials")

    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid username")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid password")

    token_data = {"sub": user.username, "role": user.role.name}
    token = create_access_token(token_data)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"Message": f"Hello, {current_user['username']} | You accessed a protected route"}


@router.patch("/users/{user_id}")
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin"])),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = payload.model_dump(exclude_unset=True)

    if "username" in update_data:
        existing = db.query(User).filter(
            User.username == update_data["username"],
            User.id != user_id,
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")
        user.username = update_data["username"]

    if "email" in update_data:
        user.email = update_data["email"]

    if "role" in update_data:
        role = db.query(Role).filter(Role.name == update_data["role"]).first()
        if not role:
            raise HTTPException(status_code=400, detail="Invalid role")
        user.role_id = role.id

    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
    }


@router.post("/users/{user_id}/change-password")
def change_password(
    user_id: int,
    payload: PasswordChange,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user["username"] != user.username and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permission")

    if not verify_password(payload.current_password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    user.hashed_password = hash_password(payload.new_password)
    db.commit()

    return {"message": "Password updated successfully"}


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin"])),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": f"User '{user.username}' deleted successfully"}


@router.post("/roles", response_model=RoleOut)
def create_role(
    payload: RoleCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin"])),
):
    existing = db.query(Role).filter(Role.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Role already exists")

    new_role = Role(name=payload.name)
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role


@router.get("/roles", response_model=list[RoleOut])
def list_roles(db: Session = Depends(get_db)):
    return db.query(Role).all()


@router.delete("/roles/{role_id}")
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin"])),
):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    in_use = db.query(User).filter(User.role_id == role.id).first()
    if in_use:
        raise HTTPException(status_code=400, detail="Cannot delete a role that is assigned to a user")

    db.delete(role)
    db.commit()
    return {"message": f"Role '{role.name}' deleted"}


@router.get("/profile")
def profile(current_user: dict = Depends(get_current_user)):
    return {
        "message": f"Profile of {current_user['username']} ({current_user['role']})"
    }


@router.get("/user/dashboard")
def user_dashboard(current_user: dict = Depends(require_roles(["user"]))):
    return {"message": "Welcome User"}


@router.get("/admin/dashboard")
def admin_dashboard(current_user: dict = Depends(require_roles(["admin"]))):
    return {"message": "Welcome Admin"}

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import auth_models, schemas, utils
from auth_database import get_db
from jose import jwt
from datetime import datetime,timedelta
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from jose import JWTError

#this has to be stored in .env file
SECRET_KEY = "yEUgLlGDn4jan9ClqaxjfNNgozbppER3xTVgYW16jbQ"
ALGORITHM = "HS256" 
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data:dict):
    to_encode=data.copy()
    expire=datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp':expire})
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt

app=FastAPI()

@app.post("/signup")
def register_user(user:schemas.UserCreate,db: Session = Depends(get_db)):
    #check if the user already exists
    existing_user=db.query(auth_models.User).filter(auth_models.User.username==user.username).first()
    if existing_user:
        raise HTTPException(status_code=400,detail="User already exits")

    #hash the password
    hashed_password = utils.hash_password(user.password)

    #create new user instance 
    new_user = auth_models.User(
            username = user.username,
            email = user.email,
            hashed_password = hashed_password,
            role = user.role

    )

    #save the newly created user to database 
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    #return the value excluding password
    return{
        "id":new_user.id,
        "username":new_user.username,
        "email":new_user.email,
        "role":new_user.role
    }

@app.post("/login")
def login_user(form_data:OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):
    user = db.query(auth_models.User).filter(auth_models.User.username==form_data.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="invalid username")

    if not utils.verify_password(form_data.password,user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="invalid password")

    token_data={"sub":user.username,"role":user.role}
    token = create_access_token(token_data)
    return {"access_token":token,"token_type":"bearer"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credential",
    headers={"WWW-Authenticate": "Bearer"})

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise credential_exception

    except JWTError:
        raise credential_exception

    return {"username": username, "role": role}

@app.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"Message": f"Hello, {current_user['username']} | You accessed a protected route"}

def require_roles(allowed_roles: list[str]):
    def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")

        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permission"
            )

        return current_user

    return role_checker

@app.patch("/users/{user_id}")
def update_user(
    user_id: int,
    payload: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin"]))
):
    user = db.query(auth_models.User).filter(auth_models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = payload.model_dump(exclude_unset=True)

    if "username" in update_data:
        existing = db.query(auth_models.User).filter(
            auth_models.User.username == update_data["username"],
            auth_models.User.id != user_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")
        user.username = update_data["username"]

    if "email" in update_data:
        user.email = update_data["email"]

    if "role" in update_data:
        user.role = update_data["role"]

    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role
    }


@app.post("/users/{user_id}/change-password")
def change_password(
    user_id: int,
    payload: schemas.PasswordChange,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user = db.query(auth_models.User).filter(auth_models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # only the user themself or an admin can change it
    if current_user["username"] != user.username and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permission")
    #even if user or admin has authority , only if they enter their old password correct, they can change it 
    if not utils.verify_password(payload.current_password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    user.hashed_password = utils.hash_password(payload.new_password)
    db.commit()

    return {"message": "Password updated successfully"}


@app.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles(["admin"]))
):
    user = db.query(auth_models.User).filter(auth_models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": f"User '{user.username}' deleted successfully"}




@app.get("/profile")
def profile(current_user: dict = Depends(require_roles(["user", "admin"]))):
    return {
        "message": f"Profile of {current_user['username']} ({current_user['role']})"
    }


@app.get("/user/dashboard")
def user_dashboard(current_user: dict = Depends(require_roles(["user"]))):
    return {"message": "Welcome User"}


@app.get("/admin/dashboard")
def admin_dashboard(current_user: dict = Depends(require_roles(["admin"]))):
    return {"message": "Welcome Admin"}


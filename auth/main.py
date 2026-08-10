from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import auth_models, schemas, utils
from auth_database import get_db
from jose import jwt
from datetime import datetime,timedelta
from fastapi.security import OAuth2PasswordRequestForm

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


from passlib.context import CryptContext
import os
from auth.models import *
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, FastAPI, HTTPException, status
from initializers.initialize_db import initialize_db

db=initialize_db()
collection=db.users
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM =  os.getenv('ALGORITHM')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


app=FastAPI()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str):
    user_data=collection.find_one({"username":username})
    if not user_data:
        return None
    return UserPrivate(**user_data)
    
def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=10)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                         detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception

        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception

    user = get_user(username=token_data.username)
    if user is None:
        raise credential_exception

    return user


async def get_current_active_user(current_user: UserPrivate = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user or Account suspended")

    return current_user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    access_token = create_access_token(
        data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=UserPublic)
async def read_users_me(current_user: UserPublic = Depends(get_current_active_user)):
    return current_user


@app.get("/users/me/uid", response_model=str)
def get_user_id(current_user:UserPublic=Depends(read_users_me)):
    # username=current_user.username
    # user=dict(collection.find_one({"username":username}))
    # user_id=user['_id']
    test='68600e91dbfd7b77a1e5cc97'
    return test



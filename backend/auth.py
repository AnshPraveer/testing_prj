from datetime import datetime, timedelta
from jose import  jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import models , schemas
from database import *
from schemas import *
from fastapi import APIRouter

# Secret and algorithm
SECRET_KEY = "dshadkjasfkvdflhasgdlfjasldfaksuhdfsahdf"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


security = HTTPBearer()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
'''
Sets up bcrypt hashing algorithm for storing hashed passwords.
'''

# Hashing & Verifying
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)


# Simple JWT functions
def create_token(user_id: str):
    payload = {"sub": user_id, "exp": datetime.now() + timedelta(hours=1)}
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(run_db)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(401, "Invalid token")

        user = db.query(models.Users).filter(models.Users.id == int(user_id)).first()
        if not user:
            raise HTTPException(401, "User not found")
        return user
    except:
        raise HTTPException(401, "Invalid token")


# Helper functions
def get_user_account(user_id: int, session: Session):
    account = session.query(models.Users).filter(models.Users.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


# Authentication API
class AuthAPI:

    @staticmethod
    async def register(user: schemas.UserCreate , db: Session = Depends(run_db)):
        # Check if email or phone already exists
        existing = db.query(models.Users).filter(
            (models.Users.email == user.email) | (models.Users.phone == user.phone)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email or phone already registered.")

        # Create user
        new_user = models.Users(
            name = user.name,
            username = user.username ,
            email = user.email,
            password = hash_password(user.password),
            phone = user.phone,
            address = user.address,
            profile_pic = user.profile_pic,
            bio = user.bio
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    async def login(user : schemas.UserLogin, db: Session = Depends(run_db)
    ):
        db_user = db.query(models.Users).filter(models.Users.email == user.email).first()
        if not db_user or not verify_password(user.password, db_user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_token(str(db_user.id))
        return {"access_token": token, "token_type": "bearer"}


## Auth Routers
auth_route = APIRouter(prefix="/auth", tags=["Authentication"])
auth_route.post("/register", response_model=UserResponse)(AuthAPI.register)
auth_route.post("/login")(AuthAPI.login)
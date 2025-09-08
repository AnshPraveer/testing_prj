from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from schemas import *
from auth import get_current_user, hash_password, verify_password
from database import run_db
from models import Users

security = HTTPBearer()

## User's API

class UserAPI:
    @staticmethod
    async def get_all_users(db: Session = Depends(run_db), user: Users = Depends(get_current_user)):
        return db.query(Users).all()

    @staticmethod
    async def get_user_profile(user_id: int, db: Session = Depends(run_db), current_user: Users = Depends(get_current_user)):
        user = db.query(Users).filter(Users.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @staticmethod
    async def get_my_profile(db: Session = Depends(run_db), user: Users = Depends(get_current_user)):
        return user

    @staticmethod
    async def update_profile(user_data: UserUpdate, db: Session = Depends(run_db), user: Users = Depends(get_current_user)):
        if user_data.username:
            # Check if username already exists
            existing = db.query(Users).filter(Users.username == user_data.username, Users.id != user.id).first()
            if existing:
                raise HTTPException(status_code=400, detail="Username already taken")
            user.username = user_data.username
        
        if user_data.bio is not None:
            user.bio = user_data.bio
        
        if user_data.profile_pic is not None:
            user.profile_pic = user_data.profile_pic
        
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    async def update_password(password_data: PasswordUpdate, db: Session = Depends(run_db), user: Users = Depends(get_current_user)):
        if not verify_password(password_data.current_password, user.password):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        user.password = hash_password(password_data.new_password)
        db.commit()
        return {"message": "Password updated successfully"}

    @staticmethod
    async def delete_account(db: Session = Depends(run_db), user: Users = Depends(get_current_user)):
        db.delete(user)
        db.commit()
        return {"message": "Account deleted successfully"}

# User Router
user_router = APIRouter(prefix="/users", tags=["Users"])
user_router.get("/all", response_model=List[UserResponse])(UserAPI.get_all_users)
user_router.get("/me", response_model=UserResponse)(UserAPI.get_my_profile)
user_router.get("/{user_id}", response_model=UserResponse)(UserAPI.get_user_profile)
user_router.put("/me", response_model=UserResponse)(UserAPI.update_profile)
user_router.put("/password")(UserAPI.update_password)
user_router.delete("/me")(UserAPI.delete_account)



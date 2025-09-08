from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from utils import *

## USER SCHEMA

class UserBase(BaseModel):
    name: str
    username: str
    email: EmailStr
    bio: Optional[str] = None
    profile_pic: Optional[str] = None




class UserCreate(UserBase):
    password : str
    address : str
    phone : int


class UserResponse(UserBase):
    id: int
    created_at : datetime
    is_active : bool

    class Config :
        from_attributes = True

class UserUpdate(BaseModel):
    username : Optional[str] = None
    bio: Optional[str] = None
    profile_pic: Optional[str] = None




## POST SCHEMA

class PostModel(BaseModel):
    content : str

class PostCreate(PostModel):
    pass

class PostResponse(PostModel):
    id : int
    created_at : datetime
    creator : UserResponse
    class Config:
        from_attributes = True

##Comment Schema

class CommentBase(BaseModel):
    content : str

class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id : int
    created_at : datetime
    user : UserResponse

    class Config:
        from_attributes = True

## Like Schema

class LikeResponse(BaseModel):
    id : int
    created_at : datetime
    user : UserResponse
    class Config:
        from_attributes = True

## Follower Schema

class FollowerResponse(BaseModel):
    id : int
    follower_id : int
    following_id : int
    created_at : datetime
    class Config:
        from_attributes = True

## Story Schemas
class StoryBase(BaseModel):
    content_url  : str

class StoryCreate(StoryBase):
    pass

class StoryResponse(StoryBase):
    id : int
    created_at : datetime
    expire_at : datetime
    is_active : bool
    user  : UserResponse
    class Config:
        from_attributes = True

## Password
class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str =  password_field()

## Login
class UserLogin (BaseModel):
    email : str
    password : str = password_field()


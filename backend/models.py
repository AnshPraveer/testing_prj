from datetime import datetime, timezone
from sqlalchemy import Integer, String, ForeignKey, Column, DateTime, Boolean, Text , BIGINT
from sqlalchemy.orm import relationship
from database import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    phone = Column(BIGINT, unique=True, nullable=False)
    address = Column(String, nullable=False)
    profile_pic = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    ## relationships
    posts = relationship("Post", back_populates="creator", cascade="all, delete")
    comments = relationship("Comment", back_populates="user", cascade="all, delete")
    likes = relationship("Like", back_populates="user", cascade="all, delete")
    stories = relationship("Story", back_populates="user", cascade="all, delete")

class Post(Base):

    __tablename__ = "post"
    id = Column(Integer,primary_key=True,index=True)
    user_id = Column(Integer, ForeignKey("users.id",ondelete="CASCADE"))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    ## relationships
    creator = relationship("Users", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete")
    likes = relationship("Like", back_populates="post", cascade="all, delete")


class Comment(Base):
    __tablename__ = "comment"
    id = Column(Integer,primary_key=True,index=True)
    user_id = Column(Integer, ForeignKey("users.id",ondelete="CASCADE"))
    post_id = Column(Integer, ForeignKey("post.id", ondelete="CASCADE"))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    ## relationships
    user = relationship("Users", back_populates="comments")
    post = relationship("Post", back_populates="comments")


class Like(Base):
    __tablename__ = "like"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    post_id = Column(Integer, ForeignKey("post.id", ondelete="CASCADE"))

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # relationships
    user = relationship("Users", back_populates="likes")
    post = relationship("Post", back_populates="likes")


class Follower(Base):
    __tablename__ = "follower"
    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id",ondelete="CASCADE"))
    following_id = Column(Integer, ForeignKey("users.id",ondelete="CASCADE"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Story(Base):
    __tablename__ = "story"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    content_url = Column(String,nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expire_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    ## relationship
    user  = relationship("Users", back_populates="stories")






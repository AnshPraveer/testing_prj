from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas import *
from auth import get_current_user
from database import run_db
from models import Users, Post, Comment

## Comments API

class CommentAPI:
    @staticmethod
    async def create_comment(post_id: int, comment_data: CommentCreate, db: Session = Depends(run_db), user: Users = Depends(get_current_user)):
        # Check if post exists
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        new_comment = Comment(
            content=comment_data.content,
            user_id=user.id,
            post_id=post_id
        )
        db.add(new_comment)
        db.commit()
        db.refresh(new_comment)
        return new_comment

    @staticmethod
    async def get_post_comments(post_id: int, skip: int = 0, limit: int = 50, db: Session = Depends(run_db), user: Users = Depends(get_current_user)):
        # Check if post exists
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        comments = db.query(Comment).filter(Comment.post_id == post_id).offset(skip).limit(limit).all()
        return comments

    @staticmethod
    async def get_my_comments(skip: int = 0, limit: int = 50, db: Session = Depends(run_db), user: Users = Depends(get_current_user)):
        comments = db.query(Comment).filter(Comment.user_id == user.id).offset(skip).limit(limit).all()
        return comments

    @staticmethod
    async def update_comment(comment_id: int, comment_data: CommentCreate, db: Session = Depends(run_db), user: Users = Depends(get_current_user)):
        comment = db.query(Comment).filter(Comment.id == comment_id, Comment.user_id == user.id).first()
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found or you don't have permission")
        
        comment.content = comment_data.content
        db.commit()
        db.refresh(comment)
        return comment

    @staticmethod
    async def delete_comment(comment_id: int, db: Session = Depends(run_db), user: Users = Depends(get_current_user)):
        comment = db.query(Comment).filter(Comment.id == comment_id, Comment.user_id == user.id).first()
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found or you don't have permission")
        
        db.delete(comment)
        db.commit()
        return {"message": "Comment deleted successfully"}

# Comments Router
comments_router = APIRouter(prefix="/comments", tags=["Comments"])
comments_router.post("/post/{post_id}", response_model=CommentResponse)(CommentAPI.create_comment)
comments_router.get("/post/{post_id}", response_model=List[CommentResponse])(CommentAPI.get_post_comments)
comments_router.get("/me", response_model=List[CommentResponse])(CommentAPI.get_my_comments)
comments_router.put("/{comment_id}", response_model=CommentResponse)(CommentAPI.update_comment)
comments_router.delete("/{comment_id}")(CommentAPI.delete_comment)
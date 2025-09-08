from typing import List
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas import *
from auth import get_current_user
from database import run_db
from models import Users, Story

## Stories API

class StoryAPI:
    @staticmethod
    async def create_story(story_data: StoryCreate, db: Session = Depends(run_db), user: Users = Depends(get_current_user)):
        # Stories expire after 24 hours
        expire_time = datetime.now(timezone.utc) + timedelta(hours=24)
        
        new_story = Story(
            content_url=story_data.content_url,
            user_id=user.id,
            expire_at=expire_time
        )
        db.add(new_story)
        db.commit()
        db.refresh(new_story)
        return new_story

    @staticmethod
    async def get_active_stories(skip: int = 0, limit: int = 50, db: Session = Depends(run_db), user: Users = Depends(get_current_user)):
        current_time = datetime.now(timezone.utc)
        stories = db.query(Story).filter(
            Story.is_active == True,
            Story.expire_at > current_time
        ).offset(skip).limit(limit).all()
        return stories

    @staticmethod
    async def get_user_stories(user_id: int, skip: int = 0, limit: int = 20, db: Session = Depends(run_db), current_user: Users = Depends(get_current_user)):
        # Check if user exists
        user = db.query(Users).filter(Users.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        current_time = datetime.now(timezone.utc)
        stories = db.query(Story).filter(
            Story.user_id == user_id,
            Story.is_active == True,
            Story.expire_at > current_time
        ).offset(skip).limit(limit).all()
        return stories

    @staticmethod
    async def get_my_stories(skip: int = 0, limit: int = 20, db: Session = Depends(run_db), user: Users = Depends(get_current_user)):
        stories = db.query(Story).filter(Story.user_id == user.id).offset(skip).limit(limit).all()
        return stories

    @staticmethod
    async def get_story(story_id: int, db: Session = Depends(run_db), user: Users = Depends(get_current_user)):
        story = db.query(Story).filter(Story.id == story_id).first()
        if not story:
            raise HTTPException(status_code=404, detail="Story not found")
        
        # Check if story is still active and not expired
        current_time = datetime.now(timezone.utc)
        if not story.is_active or story.expire_at <= current_time:
            raise HTTPException(status_code=404, detail="Story is no longer available")
        
        return story

    @staticmethod
    async def delete_story(story_id: int, db: Session = Depends(run_db), user: Users = Depends(get_current_user)):
        story = db.query(Story).filter(Story.id == story_id, Story.user_id == user.id).first()
        if not story:
            raise HTTPException(status_code=404, detail="Story not found or you don't have permission")
        
        # Soft delete by setting is_active to False
        story.is_active = False
        db.commit()
        return {"message": "Story deleted successfully"}

    @staticmethod
    async def cleanup_expired_stories(db: Session = Depends(run_db)):
        """Admin endpoint to cleanup expired stories"""
        current_time = datetime.now(timezone.utc)
        expired_stories = db.query(Story).filter(Story.expire_at <= current_time, Story.is_active == True).all()
        
        for story in expired_stories:
            story.is_active = False
        
        db.commit()
        return {"message": f"Cleaned up {len(expired_stories)} expired stories"}

# Stories Router
stories_router = APIRouter(prefix="/stories", tags=["Stories"])
stories_router.post("/", response_model=StoryResponse)(StoryAPI.create_story)
stories_router.get("/", response_model=List[StoryResponse])(StoryAPI.get_active_stories)
stories_router.get("/me", response_model=List[StoryResponse])(StoryAPI.get_my_stories)
stories_router.get("/{story_id}", response_model=StoryResponse)(StoryAPI.get_story)
stories_router.get("/user/{user_id}", response_model=List[StoryResponse])(StoryAPI.get_user_stories)
stories_router.delete("/{story_id}")(StoryAPI.delete_story)
stories_router.post("/cleanup")(StoryAPI.cleanup_expired_stories)
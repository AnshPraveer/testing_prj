import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from auth import get_current_user
from database import run_db
from models import Users

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    "images": {".jpg", ".jpeg", ".png", ".gif", ".webp"},
    "videos": {".mp4", ".avi", ".mov", ".wmv", ".flv"},
    "documents": {".pdf", ".doc", ".docx", ".txt"}
}

def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()

def is_allowed_file(filename: str, file_type: str = "images") -> bool:
    ext = get_file_extension(filename)
    return ext in ALLOWED_EXTENSIONS.get(file_type, set())

## Upload API

class UploadAPI:
    @staticmethod
    async def upload_image(
        file: UploadFile = File(...),
        db: Session = Depends(run_db),
        user: Users = Depends(get_current_user)
    ):
        # Validate file type
        if not is_allowed_file(file.filename, "images"):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only images are allowed (jpg, jpeg, png, gif, webp)"
            )
        
        # Validate file size (5MB limit)
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > 5 * 1024 * 1024:  # 5MB
            raise HTTPException(status_code=400, detail="File size too large. Maximum 5MB allowed")
        
        # Generate unique filename
        file_extension = get_file_extension(file.filename)
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, "images", unique_filename)
        
        # Create images directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Return file URL
        file_url = f"/uploads/images/{unique_filename}"
        return {
            "message": "Image uploaded successfully",
            "file_url": file_url,
            "filename": unique_filename
        }

    @staticmethod
    async def upload_video(
        file: UploadFile = File(...),
        db: Session = Depends(run_db),
        user: Users = Depends(get_current_user)
    ):
        # Validate file type
        if not is_allowed_file(file.filename, "videos"):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only videos are allowed (mp4, avi, mov, wmv, flv)"
            )
        
        # Validate file size (50MB limit for videos)
        content = await file.read()
        file_size = len(content)
        
        if file_size > 50 * 1024 * 1024:  # 50MB
            raise HTTPException(status_code=400, detail="File size too large. Maximum 50MB allowed")
        
        # Generate unique filename
        file_extension = get_file_extension(file.filename)
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, "videos", unique_filename)
        
        # Create videos directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Return file URL
        file_url = f"/uploads/videos/{unique_filename}"
        return {
            "message": "Video uploaded successfully",
            "file_url": file_url,
            "filename": unique_filename
        }

    @staticmethod
    async def upload_profile_picture(
        file: UploadFile = File(...),
        db: Session = Depends(run_db),
        user: Users = Depends(get_current_user)
    ):
        # Validate file type
        if not is_allowed_file(file.filename, "images"):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only images are allowed (jpg, jpeg, png, gif, webp)"
            )
        
        # Validate file size (2MB limit for profile pictures)
        content = await file.read()
        file_size = len(content)
        
        if file_size > 2 * 1024 * 1024:  # 2MB
            raise HTTPException(status_code=400, detail="File size too large. Maximum 2MB allowed")
        
        # Generate unique filename
        file_extension = get_file_extension(file.filename)
        unique_filename = f"profile_{user.id}_{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, "profiles", unique_filename)
        
        # Create profiles directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Update user's profile picture in database
        file_url = f"/uploads/profiles/{unique_filename}"
        user.profile_pic = file_url
        db.commit()
        
        return {
            "message": "Profile picture updated successfully",
            "file_url": file_url,
            "filename": unique_filename
        }

    @staticmethod
    async def get_file(file_type: str, filename: str):
        file_path = os.path.join(UPLOAD_DIR, file_type, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(file_path)

# Upload Router
upload_router = APIRouter(prefix="/upload", tags=["Upload"])
upload_router.post("/image")(UploadAPI.upload_image)
upload_router.post("/video")(UploadAPI.upload_video)
upload_router.post("/profile-picture")(UploadAPI.upload_profile_picture)
upload_router.get("/{file_type}/{filename}")(UploadAPI.get_file)
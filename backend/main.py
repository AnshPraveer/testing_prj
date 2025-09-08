from fastapi import FastAPI
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
# Import all routers
from auth import auth_route
from users import user_router
from posts import posts_router
from comments import comments_router
from likes import likes_router
from followers import followers_router
from stories import stories_router
from upload import upload_router
from database import Base, enginess

# Create all tables
Base.metadata.create_all(bind=enginess)

app = FastAPI(
    title="Social Media Backend API",
    description="Instagram Clone - Full Featured Social Media API",
    version="1.0.0"
)
print("hello")
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include all routers
app.include_router(auth_route)
app.include_router(user_router)
app.include_router(posts_router)
app.include_router(comments_router)
app.include_router(likes_router)
app.include_router(followers_router)
app.include_router(stories_router)
app.include_router(upload_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Social Media API",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/auth",
            "users": "/users",
            "posts": "/posts",
            "comments": "/comments",
            "likes": "/likes",
            "follow": "/follow",
            "stories": "/stories",
            "upload": "/upload"
        }
    }
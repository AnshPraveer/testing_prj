from fastapi import FastAPI
from fastapi.security import HTTPBearer

from users import *

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title= "Social Media Backend API" ,
    description = "Instagram Clone"
)

security = HTTPBearer()


app.include_router(auth_route)
app.include_router(user_router)
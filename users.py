from typing import List
from schemas import *
from auth import  *
from database import *
from models import *


security = HTTPBearer()


## User's API

class AllUsers :
    @staticmethod
    async def get_all_users (db : Session = Depends(run_db) , user: str = Depends(get_current_user)):
        return db.query(Users).all()

    @staticmethod
    async def profile_pic(db : Session = Depends(run_db), user : str = Depends(get_current_user)):
        return









# Router of get_all_users

user_router = APIRouter(tags=["Users Endpoint"])
user_router.get("/All_Users",response_model= List[schemas.UserResponse ] )(AllUsers.get_all_users)



from sqlalchemy.orm import sessionmaker , declarative_base
from sqlalchemy import create_engine

# Database Url
url = "postgresql+psycopg2://postgres:admin@localhost:5432/social_media_db"

# Create Base Class
Base = declarative_base()

# Engine
enginess = create_engine(url)

# session factory
sessions = sessionmaker(bind=enginess, autoflush=False, autocommit = False)

# Database dependency function
def run_db():
    db = sessions()
    try:
        yield db
    finally:
        db.close()


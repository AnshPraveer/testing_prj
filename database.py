from sqlalchemy.orm import sessionmaker , declarative_base
from sqlalchemy import create_engine

# Database Url
url = "postgresql+psycopg2://postgres:admin@localhost:5432/social_media_db"

# Create Base Class
Base = declarative_base()

# Engine
engine = create_engine(url)

# session factory
session = sessionmaker(bind=engine, autoflush=False, autocommit = False)

# Database dependency function
# def run_db():
#     db = session()
#     try:
#         yield db
#     finally:
#         db.close()


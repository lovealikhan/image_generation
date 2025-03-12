from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:alishaheenmbutt@localhost:5432/fastapi_db")
# DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_URL="postgresql://postgres:akgdOPTIySuWSbcaBbKtkhEBKPkPxwXK@postgres.railway.internal:5432/railway"
# DATABASE_URL="postgresql://postgres:CyUQcaYvMjAGxGAYCqBqoHGIPAmLIFgK@postgres-nyie.railway.internal:5432/railway"
# Create database engine
engine = create_engine(DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

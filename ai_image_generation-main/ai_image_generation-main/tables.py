from models import Base  # Import your models
from database import engine  # Import the engine from database.py

# Create all the tables in the database
Base.metadata.create_all(bind=engine)

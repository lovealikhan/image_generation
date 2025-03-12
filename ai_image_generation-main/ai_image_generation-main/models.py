from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database import Base  # Importing the declarative base from database.py

# User model
class User(Base):
    __tablename__ = "users_signup"

    # Use UUID for the user ID
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Email field (unique and indexed)
    email = Column(String, unique=True, index=True, nullable=False)

    # Password field (hashed password will be stored)
    password = Column(String, nullable=False)

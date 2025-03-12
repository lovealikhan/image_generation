from sqlalchemy.orm import Session
from models import User
from schemas import UserCreate
from passlib.context import CryptContext

# Create a password hash context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password
def hash_password(password: str):
    return pwd_context.hash(password)

# Create new user in the database
def create_user(db: Session, user: UserCreate):
    db_user = User(email=user.email, password=hash_password(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

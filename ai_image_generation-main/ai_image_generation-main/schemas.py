from pydantic import BaseModel
import uuid

class UserCreate(BaseModel):
    email: str
    password: str

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str

    class Config:
        orm_mode = True

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from crud import create_user
from schemas import UserCreate, UserResponse
from database import get_db
from models import User
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid

app = FastAPI()
# Add CORSMiddleware to your app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins. You can specify a list of allowed domains like ['http://example.com']
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.). You can limit it, e.g., ['GET', 'POST']
    allow_headers=["*"],  # Allows all headers. You can specify specific headers like ['Content-Type']
)
# Password Hashing Context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    """Verify if the entered password matches the stored hashed password."""
    
    print(plain_password)
    print(hashed_password)
    # print(pwd_context.hash(plain_password))
    return pwd_context.verify(plain_password, hashed_password)
    # val=False
    # if plain_password==hashed_password:
    #     val=True
    # else:
    #     val=False
    # return val
class SigninRequest(BaseModel):
    email: str
    password: str
@app.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if the email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if the email ends with "@gmail.com"
    if not user.email.endswith("@gmail.com"):
        raise HTTPException(status_code=400, detail="Email must be a Gmail address")

    # Create the new user
    new_user = create_user(db=db, user=user)

    # Returning the success message with user data
    return {"id": new_user.id, "email": new_user.email}

# Signin API (with UUID)
# @app.post("/signin")
# def signin(user_data: SigninRequest, db: Session = Depends(get_db)):
#     try:
#         user_uuid = uuid.UUID(user_data.user_uuid)  # Ensure it's a valid UUID
#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid UUID format")

#     user = db.query(User).filter(User.id == user_uuid).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     return {"message": "Login successful", "uuid": str(user.id), "email": user.email}

@app.post("/signin")
def signin(user_data: SigninRequest, db: Session = Depends(get_db)):
    print(user_data.email)
    print(user_data.password)
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # if not verify_password(user_data.password, user.password):
    # # if verify_password(user_data.password, user.password)!=True: 
    #     raise HTTPException(status_code=401, detail="Invalid password")
    
    return {
        "message": "Login successful",
        "uuid": str(user.id),  # Returning UUID for future reference
        "email": user.email
        
    }



import requests
import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
from pydantic import Field
from typing import Optional


# 🔹 Cloudinary Configuration
cloudinary.config(
        cloud_name="dgjznyppw",
        api_key="974626896655694",
        api_secret="LRTz9bCgHObU2PTxY3xsoQqqSQg",
        secure=True  # Optional, for HTTPS
    )

# 🔹 Stable Diffusion API Config
SD_API_URL = "https://api.stability.ai/v2beta/stable-image/generate/sd3"
SD_API_KEY = "sk-309g8Zhipqm4lhljR9zVJxMh1CqYMBGyQxaYj3T2AnwxWwLt"


# 🔹 Request Model
class ImageGenerateRequest(BaseModel):
    user_uuid: str  # User UUID
    category: Optional[str] = None  # Optional
    subCategory: Optional[str] = None  # Optional
    listItem: str = Field(..., min_length=1)  # Required

from typing import Optional

def generate_prompt(category: Optional[str], subCategory: Optional[str], listItem: str, image_url: Optional[str] = None) -> str:
    """Generates a structured prompt based on input values, and optionally includes an image URL."""
    
    if category and subCategory:
        prompt = (f"Generate a high-quality, artistic image of {listItem} "
                  f"in the {category} category, specifically in the {subCategory} subcategory.")
    elif category:
        prompt = (f"Generate a high-quality, artistic image of {listItem} in the {category} category.")
    elif subCategory:
        prompt = (f"Generate a high-quality, artistic image of {listItem} in the {subCategory} subcategory.")
    else:
        prompt = f"Generate a high-quality, artistic image of {listItem}."
    
    if image_url:
        prompt += f" Based on the image provided at {image_url}, ensure that the generated image aligns with its content or style."

    # prompt += " Ensure the image looks artistic, detailed, and lifelike."
    prompt += "Ensure the image looks artistic, detailed."

    return prompt


def get_next_image_number(user_uuid: str) -> int:
    """Fetches the next available image number in Cloudinary for a user."""
    try:
        cloudinary_folder = f"user_images/{user_uuid}"
        response = cloudinary.api.resources(
            type="upload",
            prefix=cloudinary_folder,
            max_results=100  # Adjust if needed
        )
        
        existing_files = [res["public_id"].split("/")[-1] for res in response["resources"]]
        existing_numbers = [int(filename.split(".")[0]) for filename in existing_files if filename.split(".")[0].isdigit()]

        return max(existing_numbers, default=0) + 1  # Next available number

    except cloudinary.exceptions.Error as e:
        print(f"Cloudinary API Error: {e}")
        return 1  # If error, start from 1


@app.post("/generate-image/")
def generate_image(request: ImageGenerateRequest):
    try:
        # 🔹 Construct the prompt
        prompt = generate_prompt(request.category, request.subCategory, request.listItem)
        print(f"Generated Prompt: {prompt}")

        # 🔹 Send Image Generation Request to Stability AI
        headers = {
            "authorization": f"Bearer {SD_API_KEY}",
            "accept": "image/*"
        }
        response = requests.post(
            SD_API_URL,
            headers=headers,
            files={"none": ''},
            data={"prompt": prompt, "output_format": "jpeg"},
        )

        if response.status_code != 200:
            error_message = response.json().get("detail", "Image generation failed")
            raise HTTPException(status_code=500, detail=f"Stable Diffusion Error: {error_message}")

        # 🔹 Get the next available image number
        next_image_number = get_next_image_number(request.user_uuid)
        print(f"Next Image Number: {next_image_number}")

        # 🔹 Save Image Temporarily
        user_folder = f"./temp/{request.user_uuid}"
        os.makedirs(user_folder, exist_ok=True)
        image_filename = f"{next_image_number}.jpg"
        image_path = os.path.join(user_folder, image_filename)

        with open(image_path, "wb") as file:
            file.write(response.content)

        # 🔹 Upload to Cloudinary inside UUID folder
        cloudinary_folder = f"user_images/{request.user_uuid}"
        cloudinary_response = cloudinary.uploader.upload(
            image_path,
            folder=cloudinary_folder,
            public_id=str(next_image_number),
            overwrite=True
        )

        # 🔹 Clean up temp storage
        os.remove(image_path)

        # 🔹 Return Image URL
        return {
            "status": "success",
            "user_uuid": request.user_uuid,
            "image_url": cloudinary_response["secure_url"]
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request Error: {str(e)}")
    except cloudinary.exceptions.Error as e:
        raise HTTPException(status_code=500, detail=f"Cloudinary Upload Error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected Error: {str(e)}")



@app.get("/user-images/{user_uuid}")
def get_user_images(user_uuid: str):
    try:
        

        # Fetch all images for the user from Cloudinary
        response = cloudinary.api.resources(
            type="upload",
            prefix=f"user_images/{user_uuid}/",  # Fetch images stored in user's folder
            max_results=100  # Adjust as needed
        )

        # Log the API response for debugging
      

        if "resources" not in response or not response["resources"]:
            
            raise HTTPException(status_code=404, detail="No images found for this user")

        # Extract image URLs
        image_urls = [img["secure_url"] for img in response["resources"]]

      

        return {"images": image_urls}

    except Exception as e:
  
        raise HTTPException(status_code=500, detail="Internal server error")


from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# Base User schemas
class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Unique user email address")
    full_name: Optional[str] = Field(None, description="Full name of the user")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Plaintext password for signup")


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, description="Updated full name")
    password: Optional[str] = Field(None, min_length=6, description="New password to set")


class UserInDBBase(UserBase):
    id: int = Field(..., description="User identifier")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Enable ORM mode


class User(UserInDBBase):
    pass


class UserWithEmail(UserInDBBase):
    pass


# Recipe schemas
class RecipeBase(BaseModel):
    title: str = Field(..., description="Title of the recipe")
    description: Optional[str] = Field(None, description="Short description of the recipe")
    ingredients: Optional[str] = Field(None, description="Ingredients as text (could be JSON string in future)")
    steps: Optional[str] = Field(None, description="Step-by-step instructions")


class RecipeCreate(RecipeBase):
    pass


class RecipeUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Updated recipe title")
    description: Optional[str] = Field(None, description="Updated description")
    ingredients: Optional[str] = Field(None, description="Updated ingredients")
    steps: Optional[str] = Field(None, description="Updated steps")


class RecipeInDBBase(RecipeBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Recipe(RecipeInDBBase):
    pass

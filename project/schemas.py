"""
schemas.py
This module defines Pydantic schemas for user authentication and chat prompt validation.
Classes:
    UserBaseSchema (BaseModel):
        Base schema for user-related data.
        Fields:
            username (str): The user's username. Must be 3-80 characters long and not empty.
            password (str): The user's password. Must be up to 128 characters and not empty.
        Validators:
            not_empty: Ensures that username and password fields are not empty or whitespace.
    UserRegisterSchema (UserBaseSchema):
        Schema for user registration. Inherits all fields and validation from UserBaseSchema.
    UserLoginSchema (UserBaseSchema):
        Schema for user login. Inherits all fields and validation from UserBaseSchema.
    ChatPromptSchema (BaseModel):
        Schema for chat prompt input.
        Fields:
            prompt (str): The chat prompt. Must be up to 1000 characters and not empty.
        Validators:
            not_empty: Ensures that the prompt field is not empty or whitespace.
"""

from pydantic import BaseModel, Field, field_validator

class UserBaseSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=80)
    password: str = Field(..., max_length=128)

    @field_validator("username", "password")
    @classmethod
    def not_empty(cls, value: str, info):
        if not value.strip():
            raise ValueError(f"{info.field_name.capitalize()} cannot be empty")
        return value



class UserRegisterSchema(UserBaseSchema):
    pass


class UserLoginSchema(UserBaseSchema):
    pass

class ChatPromptSchema(BaseModel):
    prompt: str = Field(..., max_length=1000)

    @field_validator("prompt")
    @classmethod
    def not_empty(cls, value: str):
        if not value.strip():
            raise ValueError("Prompt cannot be empty.")
        return value

from pydantic import BaseModel, Field, EmailStr,validator
from datetime import datetime,date
from typing import Annotated
from bson import ObjectId
import pydantic
import struct

class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8 , max_length=15, description= "Password should be greater than 8 and less than 15 characters long")

    @validator("new_password")
    def validate_password_complexity(cls, password):
        # Implement your own password complexity checks here
        if not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
            raise ValueError("Password must contain both letters and digits")
        return password


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: EmailStr | None


class Book(BaseModel):
    title: str
    summary: str | None = Field(default=None,max_length=50,description="Summary of this book")
    genres: list[str] | None = None
    pages: int | None = None

class UpdateBook(BaseModel):
    title: str | None = None
    summary: str | None = Field(default=None,max_length=50,description="Summary of this book")
    genres: list[str] | None = None
    pages: int | None = None

class ShowAuthor(BaseModel):
    first_name: str | None = Field(default=None,max_length=31)
    last_name: str | None = Field(default=None,min_length=3)
    email: EmailStr
    age: int | None = Field(default=15, gt=14, lt=90, description="Author shouldn`t be younger than 15 and older than 90")


class UpdateAuthor(BaseModel):
    first_name: str | None = Field(default=None,max_length=31)
    last_name: str | None = Field(default=None,min_length=3)
    email: EmailStr | None =None
    age: int | None = Field(default=15, gt=14, lt=90, description="Author shouldn`t be younger than 15 and older than 90")

class AuthorBooks(ShowAuthor):
    books: list[Book] | None = []
class Author(ShowAuthor):
    password: str = Field(min_length=8 , max_length=15, description= "Password should be greater than 8 and less than 15 characters long")

    @validator("password")
    def validate_password_complexity(cls, password):
        # Implement your own password complexity checks here
        if not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password):
            raise ValueError("Password must contain both letters and digits")
        return password


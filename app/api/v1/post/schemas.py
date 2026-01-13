from calendar import c
from typing import List, Optional, Literal, Annotated
from fastapi import Form
from pydantic import BaseModel, ConfigDict, Field, field_validator, EmailStr

from app.api.v1.auth.schemas import UserPublic
from app.api.v1.categories.schemas import CategoryPublic
from .words import words




class Tag(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=30,
        description="The name of the tag (3-100 characters)",
        example="python",
    )
    
    model_config = ConfigDict(from_attributes=True)


class Autor(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=30,
        description="The name of the author",
        example="John Doe",
    )
    email: EmailStr = Field(
        ..., description="The email of the author", example="john.doe@example.com"
    )
    
    model_config = ConfigDict(from_attributes=True)


class Post(BaseModel):
    title: str
    content: str
    tags: Optional[List[Tag]] = Field(default_factory=list)  # []
    user: Optional[UserPublic] = None
    image_url: Optional[str] = None
    category: Optional[CategoryPublic] = None
    
    model_config = ConfigDict(from_attributes=True)


class PostCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=5,
        max_length=100,
        description="The title of the blog post (5-100 characters)",
        example="My first blog post",
    )
    content: Optional[str] = Field(
        default="No content yet",
        min_length=10,
        max_length=1000,
        description="The content of the blog post (5-1000 characters)",
        example="This is my first blog post (more than 5 characters)",
    )
    category_id: Optional[int] = None
    tags: List[Tag] = Field(default_factory=list)  # []
    # author: Optional[Autor] = None

    @field_validator("title")
    @classmethod
    def not_allowed_title(cls, value: str) -> str:
        lower_value = value.lower()
        for word in words:
            if word in lower_value:
                raise ValueError(f"The title contains a prohibited word: '{word}'")
        return value
    
    @classmethod
    def as_form(
        cls,
        title: Annotated[str, Form(min_length=5)],
        content: Annotated[str, Form(min_length=10)],
        category_id: Annotated[Optional[int], Form(ge=1)] = None,
        tags: Annotated[Optional[List[str]], Form()] = None,
        
        
    ):
        tag_objs = [Tag(name=t) for t in (tags or [])]
        return cls(title=title, content=content, category_id=category_id, tags=tag_objs)


class PostUpdate(BaseModel):
    title: Optional[str] = Field(
        None,
        min_length=5,
        max_length=100,
        description="The title of the blog post (5-100 characters)",
        example="My first blog post",
    )
    content: Optional[str] = None


class PostPublic(Post):
    id: int
    slug: str
    
    model_config = ConfigDict(from_attributes=True)


class PostSummary(BaseModel):
    id: int
    title: str
    
    model_config = ConfigDict(from_attributes=True)
    
class PaginatedPosts(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool
    order_by: Literal["id", "title"]
    direction: Literal["asc", "desc"]
    search: Optional[str] = None
    items : List[PostPublic]
    

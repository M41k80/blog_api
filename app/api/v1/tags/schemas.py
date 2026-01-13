from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class TagPublic(BaseModel):
    id: int
    name: str = Field(
        ...,
        min_length=2,
        max_length=30,
        description="The name of the tag (3-100 characters)",
        example="python",
    )
    
    model_config = ConfigDict(from_attributes=True)
    
    
class TagCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=30,
        description="The name of the tag (3-100 characters)",
        example="python",
    )
    
class TagUpdate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=30,
        description="The name of the tag (3-100 characters)",
        example="python",
    )
    
    
class TagWithCount(TagPublic):
    uses: int
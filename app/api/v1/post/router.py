import time
from math import ceil
from typing import Annotated, List, Literal, Optional, Union
from fastapi import APIRouter, Depends, File,Path, Query, UploadFile, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.core.db import get_db
from app.models.user import User
from .schemas import (PostPublic, PaginatedPosts, PostCreate, PostUpdate, PostSummary)
from .repository import PostRepository
from app.services.file_storage import save_uploaded_file

from app.core.security import outh2_scheme, get_current_user, require_editor, require_admin


router = APIRouter( prefix="/posts", tags=["posts"] )

# @router.get("/sync")
# def sync_endpoint():
#     print('sync endpoint started:', threading.current_thread().name)
#     time.sleep(8)
#     return {"message": "sync endpoint done"}


# @router.get("/async")
# async def async_endpoint():
#     print('async endpoint started:', threading.current_thread().name)
#     await asyncio.sleep(8)
#     return {"message": "async endpoint done"}



# def get_fake_user():
#     return {'username': 'lukas', 'role': 'admin'}


# @router.get("/me")
# def read_me(user: dict = Depends(get_fake_user)):
#     return {'user': user}


# @router.get("/secure")
# def secure_endpoint(token: str = Depends(outh2_scheme)):
#     return {"message": "access token", "token_data": token}

@router.get("", response_model=PaginatedPosts)
def list_posts(

    text: Optional[str] | None = Query(
        default=None,
        deprecated=True,
        description="Parameter deprecated, use search instead",
    ),  # params (explicit query parameters)
    query: str | None = Query(
        default=None,
        description="Search query for blog posts",
        alias="search",
        min_length=2,
        max_length=50,
        pattern=r"^[\w\sáéíóúÁÉÍÓÚüÜñÑ-]+$",
    ),
    page: int = Query(
        1,
        ge=1,
        description="The page number",
        title="Page",
        example=1,
    ),
    per_page: int = Query(
        5,
        ge=1,
        le=50,
        description="The number of posts to retrieve per page",
        title="Posts per page",
        example=5,
    ),
    order_by: Literal["id", "title"] = Query(
        "id",
        description="The field to order the results by",
        title="Order by",
        example="id",
    ),
    direction: Literal["asc", "desc"] = Query(
        "asc",
        description="The direction to order the results by",
        title="Direction",
        example="asc",
    ),
    db: Session = Depends(get_db),
    
):
    
    repository = PostRepository(db)
    query = query or None

    total, items = repository.search(query, order_by, direction, page, per_page)
    
    total_pages = ceil(total / per_page) if total > 0 else 0
    current_page = 1 if total_pages == 0 else min(page, total_pages)
        
    has_prev = current_page > 1
    has_next = current_page < total_pages if total_pages > 0 else False
    
    
    return PaginatedPosts(
        page=current_page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_prev=has_prev,
        has_next=has_next,
        order_by=order_by,
        direction=direction,
        search=query,
        items=items,
    )
    
    
    
    
@router.get("/by-tags", response_model=List[PostPublic])
def filter_by_tags(
    tags: List[str] = Query(
        ...,
        min_length=2, 
        description="The tags to filter by: example: ?tags=python&tags=fastapi",
        example=["python", "fastapi"]
        ),
    db: Session = Depends(get_db)
    ):
    
    repository = PostRepository(db)
    
    return repository.by_tags(tags)
    

@router.get(
    "/{post_id}",
    response_model=Union[PostPublic, PostSummary],
    response_description="A single blog post",
)
def get_post(
    post_id: int = Path(
        ...,
        ge=1,
        title="Post ID",
        description="The ID of the blog post. Must be greater than 1.",
        example=1,
    ),
        include_content: bool = Query(default=True, description="false or true"), db: Session = Depends(get_db)):
    
    
    repository = PostRepository(db)
    post = repository.get(post_id)
    
        
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    if include_content:
        return PostPublic.model_validate(post, from_attributes=True)
        
    return PostSummary.model_validate(post, from_attributes=True)






@router.post(
    "",
    response_model=PostPublic,
    response_description="post created successfully(okay)",
    status_code=status.HTTP_201_CREATED,
)
def create_post(post: Annotated[PostCreate, Depends(PostCreate.as_form)], image: Optional[UploadFile] = File(None), db: Session = Depends(get_db), _editor: User = Depends(require_editor)):
    
    repository = PostRepository(db)
    saved = None
    try:
        if image is not None:
            saved = save_uploaded_file(image)
        image_url = saved["url"] if saved else None
        
        post = repository.create_post(
            title=post.title,
            content=post.content,
            user=_editor,
            category_id=post.category_id,
            tags=[tag.model_dump() for tag in post.tags],
            image_url=image_url
        )
        db.commit()
        db.refresh(post)
        return post
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=409, detail="Post Title already exists, please choose another title , error: " + str(e))
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error DB creating post")
    
    
    
@router.put(
    "/{post_id}",
    response_model=PostPublic,
    response_description="post updated successfully(okay)",
    response_model_exclude_none=True,
)
def update_post(post_id: int, data: PostUpdate, db: Session = Depends(get_db), _editor: User = Depends(require_editor)):
    repository = PostRepository(db)
    
    post = repository.get(post_id)
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    try:
        updates = data.model_dump(exclude_unset=True)
        post = repository.update_post(post, updates)
        db.commit()
        db.refresh(post)
        return post
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error DB updating post")
    
   


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    repository = PostRepository(db)
    post = repository.get(post_id)#se obtiene el post a eliminar
    if not post:
        raise HTTPException(status_code=404, detail="Post not found") #si no se encuentra el post se lanza una excepcion
    
    try:
        repository.delete_post(post) #se elimina el post
        db.commit() #se confirma la eliminacion
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error DB deleting post")
    

@router.get("/post/{slug}", response_model=Union[PostPublic, PostSummary])
def post_by_slug(slug: str, include_content: bool = Query(default=True, description="include content or not"), db: Session = Depends(get_db)):
    repository = PostRepository(db)
    post = repository.get_by_slug(slug)
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    if include_content:
        return PostPublic.model_validate(post, from_attributes=True)

    return PostSummary.model_validate(post, from_attributes=True)
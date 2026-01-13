from annotated_types import T
from fastapi import Query
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.api.v1.tags.repository import TagRepository
from app.core.db import get_db

from app.api.v1.tags.schemas import TagCreate, TagPublic, TagUpdate
from app.core.security import get_current_user, require_admin, require_editor, require_user
from app.models.user import User

router = APIRouter(prefix="/tags", tags=["tags"])

@router.get('', response_model=dict)
def list_tags(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    oder_by: str = Query('id', pattern=r'^(id|name)'),
    direction: str = Query('asc', pattern=r'^(asc|desc)'),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
    
):
    
    repository = TagRepository(db)
    return repository.list_tags(
        page=page,
        per_page=per_page,
        order_by=oder_by,
        direction=direction,
        search=search,
    )

@router.post('', response_model=TagPublic, response_description="POST created successfully(okay)", status_code=status.HTTP_201_CREATED)
def create_tag(tag: TagCreate, db: Session = Depends(get_db), _editor: User = Depends(require_editor)):
    repository = TagRepository(db)
    try:
        tag_created = repository.create_tag(name = tag.name)
        db.commit()
        db.refresh(tag_created)
        return tag_created
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error DB creating tag")
        
@router.put('/{tag_id}', response_model=TagPublic, response_description="PUT updated successfully(okay)", status_code=status.HTTP_200_OK)
def update_tag(
    tag_id: int,
    payload: TagUpdate,
    db: Session = Depends(get_db),
    _editor: User = Depends(require_editor),
    ):
    repository = TagRepository(db)
    try:
        tag_updated = repository.update(tag_id, name = payload.name)
        if not tag_updated:
            raise HTTPException(status_code=404, detail="Tag not found")
        
        db.commit()
        return TagPublic.model_validate(tag_updated)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error DB updating tag")
        
@router.delete('/{tag_id}', response_description="DELETE deleted successfully(okay)", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(require_user),
    ):
    repository = TagRepository(db)
    try:
        tag_deleted = repository.delete(tag_id)
        if not tag_deleted:
            raise HTTPException(status_code=404, detail="Tag not found")
        db.commit()
        return None
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error DB deleting tag")

@router.get('/popular/top')
def get_most_popular(
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    repository = TagRepository(db)
    row = repository.most_popular()
    
    if not row:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    return TagPublic.model_validate(row)
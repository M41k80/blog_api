import re
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, UniqueConstraint, func, null, select, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

from datetime import datetime

if TYPE_CHECKING:
    from .user import User
    from app.models.tag import TagORM
    from .category import CategoryORM



post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", ForeignKey("post.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
    
)


    



class PostORM(Base):
    __tablename__ = "post"
    __table_args__ = (UniqueConstraint("title", "content", name="unique_post_title"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(300), nullable=True)
    create_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    user: Mapped[Optional["User"]] = relationship(back_populates="posts")
    
    
    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    category = relationship("CategoryORM", back_populates="posts")

    tags: Mapped[List["TagORM"]] = relationship(secondary=post_tags, back_populates="posts", lazy="selectin",passive_deletes=True)
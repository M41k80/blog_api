from app.core.db import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String



class CategoryORM(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    slug:Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    
    posts = relationship("PostORM", back_populates="category", cascade="all, delete", passive_deletes=True)
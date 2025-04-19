from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from app.db.base_class import Base
from app.models.content import ContentType

class ContentTemplate(Base):
    __tablename__ = "content_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    content_type = Column(Enum(ContentType), nullable=False)
    template = Column(String, nullable=False)
    variables = Column(String)  # Stored as JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 
from typing import Any, Dict, Optional, Union
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.content import ContentTemplate
from app.schemas.content import ContentTemplateCreate, ContentTemplateUpdate
import json

class CRUDContentTemplate(CRUDBase[ContentTemplate, ContentTemplateCreate, ContentTemplateUpdate]):
    def create(self, db: Session, *, obj_in: ContentTemplateCreate) -> ContentTemplate:
        obj_in_data = obj_in.dict()
        obj_in_data["variables"] = json.dumps(obj_in_data["variables"])
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ContentTemplate,
        obj_in: Union[ContentTemplateUpdate, Dict[str, Any]]
    ) -> ContentTemplate:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if "variables" in update_data:
            update_data["variables"] = json.dumps(update_data["variables"])
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[ContentTemplate]:
        return (
            db.query(self.model)
            .offset(skip)
            .limit(limit)
            .all()
        )

content_template = CRUDContentTemplate(ContentTemplate) 
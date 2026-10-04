from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import current_user
from ..models import User
from ..services import analytics as svc

router = APIRouter(tags=["analytics"])


@router.get("/progress")
def progress(user: User = Depends(current_user), db: Session = Depends(get_db)):
    out = svc.progress(db, user)
    db.commit()
    return out


@router.get("/analytics")
def analytics(user: User = Depends(current_user), db: Session = Depends(get_db)):
    out = svc.analytics(db, user)
    db.commit()
    return out

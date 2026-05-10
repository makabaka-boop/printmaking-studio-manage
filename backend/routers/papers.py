from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Paper
from schemas import PaperCreate, PaperOut, PaperAlertItem

router = APIRouter(prefix="/papers", tags=["纸张耗材"])


@router.get("/", response_model=List[PaperOut])
def list_papers(db: Session = Depends(get_db)):
    return db.query(Paper).order_by(Paper.id.desc()).all()


@router.post("/", response_model=PaperOut)
def create_paper(data: PaperCreate, db: Session = Depends(get_db)):
    item = Paper(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{paper_id}", response_model=PaperOut)
def get_paper(paper_id: int, db: Session = Depends(get_db)):
    item = db.query(Paper).filter(Paper.id == paper_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="纸张不存在")
    return item


@router.put("/{paper_id}", response_model=PaperOut)
def update_paper(paper_id: int, data: PaperCreate, db: Session = Depends(get_db)):
    item = db.query(Paper).filter(Paper.id == paper_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="纸张不存在")
    for k, v in data.model_dump().items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{paper_id}")
def delete_paper(paper_id: int, db: Session = Depends(get_db)):
    item = db.query(Paper).filter(Paper.id == paper_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="纸张不存在")
    db.delete(item)
    db.commit()
    return {"ok": True}


@router.get("/alerts/list", response_model=List[PaperAlertItem])
def paper_alerts(db: Session = Depends(get_db)):
    return db.query(Paper).filter(Paper.stock <= Paper.threshold).all()

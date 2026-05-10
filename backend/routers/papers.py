from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database.database import get_db
from backend.models import models
from backend.schemas import schemas

router = APIRouter(prefix="/api/papers", tags=["纸张库存"])

@router.get("/", response_model=List[schemas.Paper])
def get_papers(low_stock: bool = False, db: Session = Depends(get_db)):
    query = db.query(models.Paper)
    papers = query.all()
    result = []
    for paper in papers:
        is_low = paper.stock < paper.threshold
        if low_stock and not is_low:
            continue
        result.append(schemas.Paper(
            id=paper.id,
            name=paper.name,
            weight=paper.weight,
            size=paper.size,
            stock=paper.stock,
            cost_per_sheet=paper.cost_per_sheet,
            threshold=paper.threshold,
            created_at=paper.created_at,
            is_low_stock=is_low
        ))
    return result

@router.get("/{paper_id}", response_model=schemas.Paper)
def get_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = db.query(models.Paper).filter(models.Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="纸张不存在")
    return schemas.Paper(
        id=paper.id,
        name=paper.name,
        weight=paper.weight,
        size=paper.size,
        stock=paper.stock,
        cost_per_sheet=paper.cost_per_sheet,
        threshold=paper.threshold,
        created_at=paper.created_at,
        is_low_stock=paper.stock < paper.threshold
    )

@router.post("/", response_model=schemas.Paper)
def create_paper(paper: schemas.PaperCreate, db: Session = Depends(get_db)):
    db_paper = models.Paper(**paper.dict())
    db.add(db_paper)
    db.commit()
    db.refresh(db_paper)
    return schemas.Paper(
        id=db_paper.id,
        name=db_paper.name,
        weight=db_paper.weight,
        size=db_paper.size,
        stock=db_paper.stock,
        cost_per_sheet=db_paper.cost_per_sheet,
        threshold=db_paper.threshold,
        created_at=db_paper.created_at,
        is_low_stock=db_paper.stock < db_paper.threshold
    )

@router.put("/{paper_id}", response_model=schemas.Paper)
def update_paper(paper_id: int, paper_update: schemas.PaperUpdate, db: Session = Depends(get_db)):
    db_paper = db.query(models.Paper).filter(models.Paper.id == paper_id).first()
    if not db_paper:
        raise HTTPException(status_code=404, detail="纸张不存在")
    for key, value in paper_update.dict(exclude_unset=True).items():
        setattr(db_paper, key, value)
    db.commit()
    db.refresh(db_paper)
    return schemas.Paper(
        id=db_paper.id,
        name=db_paper.name,
        weight=db_paper.weight,
        size=db_paper.size,
        stock=db_paper.stock,
        cost_per_sheet=db_paper.cost_per_sheet,
        threshold=db_paper.threshold,
        created_at=db_paper.created_at,
        is_low_stock=db_paper.stock < db_paper.threshold
    )

@router.delete("/{paper_id}")
def delete_paper(paper_id: int, db: Session = Depends(get_db)):
    db_paper = db.query(models.Paper).filter(models.Paper.id == paper_id).first()
    if not db_paper:
        raise HTTPException(status_code=404, detail="纸张不存在")
    db.delete(db_paper)
    db.commit()
    return {"message": "删除成功"}

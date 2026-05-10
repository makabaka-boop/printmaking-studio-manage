from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database.database import get_db
from backend.models import models
from backend.schemas import schemas

router = APIRouter(prefix="/api/artworks", tags=["作品管理"])

@router.get("/", response_model=List[schemas.Artwork])
def get_artworks(db: Session = Depends(get_db)):
    artworks = db.query(models.Artwork).all()
    result = []
    for artwork in artworks:
        total_good = sum(batch.good_prints for batch in artwork.batches)
        result.append(schemas.Artwork(
            id=artwork.id,
            name=artwork.name,
            print_type=artwork.print_type,
            finished_size=artwork.finished_size,
            planned_edition=artwork.planned_edition,
            signature_rule=artwork.signature_rule,
            created_at=artwork.created_at,
            sold_edition=total_good,
            remaining_edition=artwork.planned_edition - total_good
        ))
    return result

@router.get("/{artwork_id}", response_model=schemas.Artwork)
def get_artwork(artwork_id: int, db: Session = Depends(get_db)):
    artwork = db.query(models.Artwork).filter(models.Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(status_code=404, detail="作品不存在")
    total_good = sum(batch.good_prints for batch in artwork.batches)
    return schemas.Artwork(
        id=artwork.id,
        name=artwork.name,
        print_type=artwork.print_type,
        finished_size=artwork.finished_size,
        planned_edition=artwork.planned_edition,
        signature_rule=artwork.signature_rule,
        created_at=artwork.created_at,
        sold_edition=total_good,
        remaining_edition=artwork.planned_edition - total_good
    )

@router.post("/", response_model=schemas.Artwork)
def create_artwork(artwork: schemas.ArtworkCreate, db: Session = Depends(get_db)):
    db_artwork = models.Artwork(**artwork.dict())
    db.add(db_artwork)
    db.commit()
    db.refresh(db_artwork)
    return schemas.Artwork(
        id=db_artwork.id,
        name=db_artwork.name,
        print_type=db_artwork.print_type,
        finished_size=db_artwork.finished_size,
        planned_edition=db_artwork.planned_edition,
        signature_rule=db_artwork.signature_rule,
        created_at=db_artwork.created_at,
        sold_edition=0,
        remaining_edition=db_artwork.planned_edition
    )

@router.put("/{artwork_id}", response_model=schemas.Artwork)
def update_artwork(artwork_id: int, artwork_update: schemas.ArtworkUpdate, db: Session = Depends(get_db)):
    db_artwork = db.query(models.Artwork).filter(models.Artwork.id == artwork_id).first()
    if not db_artwork:
        raise HTTPException(status_code=404, detail="作品不存在")
    for key, value in artwork_update.dict(exclude_unset=True).items():
        setattr(db_artwork, key, value)
    db.commit()
    db.refresh(db_artwork)
    total_good = sum(batch.good_prints for batch in db_artwork.batches)
    return schemas.Artwork(
        id=db_artwork.id,
        name=db_artwork.name,
        print_type=db_artwork.print_type,
        finished_size=db_artwork.finished_size,
        planned_edition=db_artwork.planned_edition,
        signature_rule=db_artwork.signature_rule,
        created_at=db_artwork.created_at,
        sold_edition=total_good,
        remaining_edition=db_artwork.planned_edition - total_good
    )

@router.delete("/{artwork_id}")
def delete_artwork(artwork_id: int, db: Session = Depends(get_db)):
    db_artwork = db.query(models.Artwork).filter(models.Artwork.id == artwork_id).first()
    if not db_artwork:
        raise HTTPException(status_code=404, detail="作品不存在")
    db.delete(db_artwork)
    db.commit()
    return {"message": "删除成功"}

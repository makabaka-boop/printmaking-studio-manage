from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Artwork, Plate, PrintBatch
from schemas import ArtworkCreate, ArtworkOut, PlateCreate, PlateOut

router = APIRouter(prefix="/artworks", tags=["作品档案"])


@router.get("/", response_model=List[ArtworkOut])
def list_artworks(db: Session = Depends(get_db)):
    return db.query(Artwork).order_by(Artwork.id.desc()).all()


@router.post("/", response_model=ArtworkOut)
def create_artwork(data: ArtworkCreate, db: Session = Depends(get_db)):
    item = Artwork(**data.model_dump(), remaining_edition=data.planned_edition)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{artwork_id}", response_model=ArtworkOut)
def get_artwork(artwork_id: int, db: Session = Depends(get_db)):
    item = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="作品不存在")
    return item


@router.put("/{artwork_id}", response_model=ArtworkOut)
def update_artwork(artwork_id: int, data: ArtworkCreate, db: Session = Depends(get_db)):
    item = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="作品不存在")
    used_edition = item.planned_edition - item.remaining_edition
    for k, v in data.model_dump().items():
        setattr(item, k, v)
    item.remaining_edition = data.planned_edition - used_edition
    if item.remaining_edition < 0:
        item.remaining_edition = 0
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{artwork_id}")
def delete_artwork(artwork_id: int, db: Session = Depends(get_db)):
    item = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="作品不存在")
    db.delete(item)
    db.commit()
    return {"ok": True}


@router.get("/{artwork_id}/plates", response_model=List[PlateOut])
def list_plates(artwork_id: int, db: Session = Depends(get_db)):
    return db.query(Plate).filter(Plate.artwork_id == artwork_id).order_by(Plate.color_order).all()


@router.post("/{artwork_id}/plates", response_model=PlateOut)
def create_plate(artwork_id: int, data: PlateCreate, db: Session = Depends(get_db)):
    item = Plate(artwork_id=artwork_id, color_order=data.color_order, ink_ratio_note=data.ink_ratio_note, is_finalized=data.is_finalized)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/plates/{plate_id}", response_model=PlateOut)
def update_plate(plate_id: int, data: PlateCreate, db: Session = Depends(get_db)):
    item = db.query(Plate).filter(Plate.id == plate_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="版次不存在")
    item.color_order = data.color_order
    item.ink_ratio_note = data.ink_ratio_note
    item.is_finalized = data.is_finalized
    db.commit()
    db.refresh(item)
    return item


@router.delete("/plates/{plate_id}")
def delete_plate(plate_id: int, db: Session = Depends(get_db)):
    item = db.query(Plate).filter(Plate.id == plate_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="版次不存在")
    db.delete(item)
    db.commit()
    return {"ok": True}

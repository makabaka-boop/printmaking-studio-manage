from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database.database import get_db
from backend.models import models
from backend.schemas import schemas

router = APIRouter(prefix="/api/plates", tags=["版次管理"])

@router.get("/", response_model=List[schemas.Plate])
def get_plates(artwork_id: int = None, db: Session = Depends(get_db)):
    query = db.query(models.Plate)
    if artwork_id:
        query = query.filter(models.Plate.artwork_id == artwork_id)
    return query.all()

@router.get("/{plate_id}", response_model=schemas.Plate)
def get_plate(plate_id: int, db: Session = Depends(get_db)):
    plate = db.query(models.Plate).filter(models.Plate.id == plate_id).first()
    if not plate:
        raise HTTPException(status_code=404, detail="版次不存在")
    return plate

@router.post("/", response_model=schemas.Plate)
def create_plate(plate: schemas.PlateCreate, db: Session = Depends(get_db)):
    artwork = db.query(models.Artwork).filter(models.Artwork.id == plate.artwork_id).first()
    if not artwork:
        raise HTTPException(status_code=404, detail="作品不存在")
    db_plate = models.Plate(**plate.dict())
    db.add(db_plate)
    db.commit()
    db.refresh(db_plate)
    return db_plate

@router.put("/{plate_id}", response_model=schemas.Plate)
def update_plate(plate_id: int, plate_update: schemas.PlateUpdate, db: Session = Depends(get_db)):
    db_plate = db.query(models.Plate).filter(models.Plate.id == plate_id).first()
    if not db_plate:
        raise HTTPException(status_code=404, detail="版次不存在")
    for key, value in plate_update.dict(exclude_unset=True).items():
        setattr(db_plate, key, value)
    db.commit()
    db.refresh(db_plate)
    return db_plate

@router.delete("/{plate_id}")
def delete_plate(plate_id: int, db: Session = Depends(get_db)):
    db_plate = db.query(models.Plate).filter(models.Plate.id == plate_id).first()
    if not db_plate:
        raise HTTPException(status_code=404, detail="版次不存在")
    db.delete(db_plate)
    db.commit()
    return {"message": "删除成功"}

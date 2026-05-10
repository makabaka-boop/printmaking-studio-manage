from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from backend.database.database import get_db
from backend.models import models
from backend.schemas import schemas

router = APIRouter(prefix="/api/batches", tags=["印制批次"])

@router.get("/", response_model=List[dict])
def get_batches(db: Session = Depends(get_db)):
    batches = db.query(models.PrintBatch).order_by(models.PrintBatch.print_date.desc()).all()
    result = []
    for batch in batches:
        plates = [bp.plate for bp in batch.plates_used]
        result.append({
            "id": batch.id,
            "artwork_id": batch.artwork_id,
            "artwork_name": batch.artwork.name,
            "print_date": batch.print_date,
            "test_prints": batch.test_prints,
            "good_prints": batch.good_prints,
            "waste_prints": batch.waste_prints,
            "paper_id": batch.paper_id,
            "paper_name": batch.paper.name if batch.paper else None,
            "paper_used": batch.paper_used,
            "notes": batch.notes,
            "created_at": batch.created_at,
            "plates": plates,
            "waste_rate": (batch.waste_prints / (batch.good_prints + batch.test_prints + batch.waste_prints) * 100) if (batch.good_prints + batch.test_prints + batch.waste_prints) > 0 else 0
        })
    return result

@router.get("/{batch_id}", response_model=dict)
def get_batch(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(models.PrintBatch).filter(models.PrintBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="批次不存在")
    plates = [bp.plate for bp in batch.plates_used]
    return {
        "id": batch.id,
        "artwork_id": batch.artwork_id,
        "artwork_name": batch.artwork.name,
        "print_date": batch.print_date,
        "test_prints": batch.test_prints,
        "good_prints": batch.good_prints,
        "waste_prints": batch.waste_prints,
        "paper_id": batch.paper_id,
        "paper_name": batch.paper.name if batch.paper else None,
        "paper_used": batch.paper_used,
        "notes": batch.notes,
        "created_at": batch.created_at,
        "plates": plates
    }

@router.post("/", response_model=dict)
def create_batch(batch: schemas.PrintBatchCreate, db: Session = Depends(get_db)):
    artwork = db.query(models.Artwork).filter(models.Artwork.id == batch.artwork_id).first()
    if not artwork:
        raise HTTPException(status_code=404, detail="作品不存在")
    
    total_prints = batch.test_prints + batch.good_prints + batch.waste_prints
    if batch.paper_id and batch.paper_used > 0:
        if batch.paper_used != total_prints:
            raise HTTPException(status_code=400, detail=f"纸张用量必须等于试印+正印+废张总数（{total_prints}张）")
    
    existing_good = sum(b.good_prints for b in artwork.batches)
    if existing_good + batch.good_prints > artwork.planned_edition:
        remaining = artwork.planned_edition - existing_good
        raise HTTPException(status_code=400, detail=f"正印数量超过计划版数，还可印制{remaining}张正印")
    
    db_batch = models.PrintBatch(
        artwork_id=batch.artwork_id,
        print_date=batch.print_date,
        test_prints=batch.test_prints,
        good_prints=batch.good_prints,
        waste_prints=batch.waste_prints,
        paper_id=batch.paper_id,
        paper_used=batch.paper_used,
        notes=batch.notes
    )
    db.add(db_batch)
    db.flush()
    
    for plate_id in batch.plates:
        plate = db.query(models.Plate).filter(models.Plate.id == plate_id).first()
        if plate:
            db_batch_plate = models.BatchPlate(batch_id=db_batch.id, plate_id=plate_id)
            db.add(db_batch_plate)
    
    if batch.paper_id and batch.paper_used > 0:
        paper = db.query(models.Paper).filter(models.Paper.id == batch.paper_id).first()
        if paper:
            if paper.stock < batch.paper_used:
                raise HTTPException(status_code=400, detail=f"纸张库存不足，当前库存：{paper.stock}")
            paper.stock -= batch.paper_used
    
    db.commit()
    db.refresh(db_batch)
    
    plates = [bp.plate for bp in db_batch.plates_used]
    return {
        "id": db_batch.id,
        "artwork_id": db_batch.artwork_id,
        "artwork_name": db_batch.artwork.name,
        "print_date": db_batch.print_date,
        "test_prints": db_batch.test_prints,
        "good_prints": db_batch.good_prints,
        "waste_prints": db_batch.waste_prints,
        "paper_id": db_batch.paper_id,
        "paper_name": db_batch.paper.name if db_batch.paper else None,
        "paper_used": db_batch.paper_used,
        "notes": db_batch.notes,
        "created_at": db_batch.created_at,
        "plates": plates
    }

@router.put("/{batch_id}", response_model=dict)
def update_batch(batch_id: int, batch_update: schemas.PrintBatchUpdate, db: Session = Depends(get_db)):
    db_batch = db.query(models.PrintBatch).filter(models.PrintBatch.id == batch_id).first()
    if not db_batch:
        raise HTTPException(status_code=404, detail="批次不存在")
    
    old_paper_used = db_batch.paper_used
    old_paper_id = db_batch.paper_id
    old_good_prints = db_batch.good_prints
    
    update_data = batch_update.dict(exclude_unset=True)
    plates_to_update = update_data.pop('plates', None)
    
    new_test_prints = batch_update.test_prints if batch_update.test_prints is not None else db_batch.test_prints
    new_good_prints = batch_update.good_prints if batch_update.good_prints is not None else db_batch.good_prints
    new_waste_prints = batch_update.waste_prints if batch_update.waste_prints is not None else db_batch.waste_prints
    total_prints = new_test_prints + new_good_prints + new_waste_prints
    
    new_paper_id = batch_update.paper_id if batch_update.paper_id is not None else old_paper_id
    new_paper_used = batch_update.paper_used if batch_update.paper_used is not None else old_paper_used
    
    if new_paper_id and new_paper_used > 0:
        if new_paper_used != total_prints:
            raise HTTPException(status_code=400, detail=f"纸张用量必须等于试印+正印+废张总数（{total_prints}张）")
    
    artwork = db.query(models.Artwork).filter(models.Artwork.id == db_batch.artwork_id).first()
    if artwork and batch_update.good_prints is not None:
        existing_good = sum(b.good_prints for b in artwork.batches if b.id != batch_id)
        if existing_good + new_good_prints > artwork.planned_edition:
            remaining = artwork.planned_edition - existing_good
            raise HTTPException(status_code=400, detail=f"正印数量超过计划版数，还可印制{remaining}张正印")
    
    for key, value in update_data.items():
        setattr(db_batch, key, value)
    
    if plates_to_update is not None:
        for bp in db_batch.plates_used:
            db.delete(bp)
        for plate_id in plates_to_update:
            plate = db.query(models.Plate).filter(models.Plate.id == plate_id).first()
            if plate:
                db_batch_plate = models.BatchPlate(batch_id=db_batch.id, plate_id=plate_id)
                db.add(db_batch_plate)
    
    if batch_update.paper_used is not None or batch_update.paper_id is not None:
        if old_paper_id and old_paper_used > 0:
            old_paper = db.query(models.Paper).filter(models.Paper.id == old_paper_id).first()
            if old_paper:
                old_paper.stock += old_paper_used
        
        if new_paper_id and new_paper_used > 0:
            new_paper = db.query(models.Paper).filter(models.Paper.id == new_paper_id).first()
            if new_paper:
                if new_paper.stock < new_paper_used:
                    raise HTTPException(status_code=400, detail=f"纸张库存不足，当前库存：{new_paper.stock}")
                new_paper.stock -= new_paper_used
    
    db.commit()
    db.refresh(db_batch)
    
    plates = [bp.plate for bp in db_batch.plates_used]
    return {
        "id": db_batch.id,
        "artwork_id": db_batch.artwork_id,
        "artwork_name": db_batch.artwork.name,
        "print_date": db_batch.print_date,
        "test_prints": db_batch.test_prints,
        "good_prints": db_batch.good_prints,
        "waste_prints": db_batch.waste_prints,
        "paper_id": db_batch.paper_id,
        "paper_name": db_batch.paper.name if db_batch.paper else None,
        "paper_used": db_batch.paper_used,
        "notes": db_batch.notes,
        "created_at": db_batch.created_at,
        "plates": plates
    }

@router.delete("/{batch_id}")
def delete_batch(batch_id: int, db: Session = Depends(get_db)):
    db_batch = db.query(models.PrintBatch).filter(models.PrintBatch.id == batch_id).first()
    if not db_batch:
        raise HTTPException(status_code=404, detail="批次不存在")
    
    if db_batch.paper_id and db_batch.paper_used > 0:
        paper = db.query(models.Paper).filter(models.Paper.id == db_batch.paper_id).first()
        if paper:
            paper.stock += db_batch.paper_used
    
    db.delete(db_batch)
    db.commit()
    return {"message": "删除成功"}

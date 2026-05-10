from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import PrintBatch, BatchPlateUsage, Artwork, Paper
from schemas import PrintBatchCreate, PrintBatchOut

router = APIRouter(prefix="/batches", tags=["印制批次"])


@router.get("/", response_model=List[PrintBatchOut])
def list_batches(db: Session = Depends(get_db)):
    return db.query(PrintBatch).order_by(PrintBatch.id.desc()).all()


@router.post("/", response_model=PrintBatchOut)
def create_batch(data: PrintBatchCreate, db: Session = Depends(get_db)):
    artwork = db.query(Artwork).filter(Artwork.id == data.artwork_id).first()
    if not artwork:
        raise HTTPException(status_code=404, detail="作品不存在")
    paper = db.query(Paper).filter(Paper.id == data.paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="纸张不存在")

    if paper.stock < data.paper_consumed:
        raise HTTPException(status_code=400, detail=f"纸张库存不足，当前库存 {paper.stock}")

    paper.stock -= data.paper_consumed

    if artwork.remaining_edition < data.official_count:
        raise HTTPException(status_code=400, detail=f"剩余可售版数不足，当前剩余 {artwork.remaining_edition}")
    artwork.remaining_edition -= data.official_count

    batch = PrintBatch(
        artwork_id=data.artwork_id,
        date=data.date,
        trial_count=data.trial_count,
        official_count=data.official_count,
        waste_count=data.waste_count,
        paper_id=data.paper_id,
        paper_name_snapshot=paper.name,
        paper_consumed=data.paper_consumed,
        note=data.note,
    )
    db.add(batch)
    db.flush()

    for pid in data.plate_ids:
        usage = BatchPlateUsage(batch_id=batch.id, plate_id=pid)
        db.add(usage)

    db.commit()
    db.refresh(batch)
    return batch


@router.get("/{batch_id}", response_model=PrintBatchOut)
def get_batch(batch_id: int, db: Session = Depends(get_db)):
    item = db.query(PrintBatch).filter(PrintBatch.id == batch_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="批次不存在")
    return item


@router.delete("/{batch_id}")
def delete_batch(batch_id: int, db: Session = Depends(get_db)):
    item = db.query(PrintBatch).filter(PrintBatch.id == batch_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="批次不存在")

    artwork = db.query(Artwork).filter(Artwork.id == item.artwork_id).first()
    if artwork:
        artwork.remaining_edition += item.official_count

    paper = db.query(Paper).filter(Paper.id == item.paper_id).first()
    if paper:
        paper.stock += item.paper_consumed

    db.delete(item)
    db.commit()
    return {"ok": True}

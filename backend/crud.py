from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import date, timedelta
import models
import schemas


def get_artwork(db: Session, artwork_id: int):
    artwork = db.query(models.Artwork).filter(models.Artwork.id == artwork_id).first()
    if artwork:
        artwork.remaining_edition = artwork.planned_edition - artwork.sold_count
    return artwork


def get_artworks(db: Session, skip: int = 0, limit: int = 100):
    artworks = db.query(models.Artwork).offset(skip).limit(limit).all()
    for artwork in artworks:
        artwork.remaining_edition = artwork.planned_edition - artwork.sold_count
    return artworks


def create_artwork(db: Session, artwork: schemas.ArtworkCreate):
    db_artwork = models.Artwork(
        **artwork.model_dump(),
        created_at=date.today()
    )
    db.add(db_artwork)
    db.commit()
    db.refresh(db_artwork)
    db_artwork.remaining_edition = db_artwork.planned_edition - db_artwork.sold_count
    return db_artwork


def delete_artwork(db: Session, artwork_id: int):
    db_artwork = db.query(models.Artwork).filter(models.Artwork.id == artwork_id).first()
    if db_artwork:
        db.query(models.Plate).filter(models.Plate.artwork_id == artwork_id).delete()
        db.query(models.PrintBatch).filter(models.PrintBatch.artwork_id == artwork_id).delete()
        db.delete(db_artwork)
        db.commit()
        return True
    return False


def get_plate(db: Session, plate_id: int):
    return db.query(models.Plate).filter(models.Plate.id == plate_id).first()


def get_plates_by_artwork(db: Session, artwork_id: int):
    return db.query(models.Plate).filter(models.Plate.artwork_id == artwork_id).all()


def get_plates(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Plate).offset(skip).limit(limit).all()


def create_plate(db: Session, plate: schemas.PlateCreate):
    db_plate = models.Plate(**plate.model_dump())
    db.add(db_plate)
    db.commit()
    db.refresh(db_plate)
    return db_plate


def update_plate(db: Session, plate_id: int, plate_update: schemas.PlateUpdate):
    db_plate = db.query(models.Plate).filter(models.Plate.id == plate_id).first()
    if db_plate:
        update_data = plate_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_plate, key, value)
        db.commit()
        db.refresh(db_plate)
    return db_plate


def delete_plate(db: Session, plate_id: int):
    db_plate = db.query(models.Plate).filter(models.Plate.id == plate_id).first()
    if db_plate:
        db.delete(db_plate)
        db.commit()
        return True
    return False


def get_paper(db: Session, paper_id: int):
    paper = db.query(models.Paper).filter(models.Paper.id == paper_id).first()
    if paper:
        paper.is_low_stock = paper.stock_count <= paper.threshold
    return paper


def get_papers(db: Session, skip: int = 0, limit: int = 100):
    papers = db.query(models.Paper).offset(skip).limit(limit).all()
    for paper in papers:
        paper.is_low_stock = paper.stock_count <= paper.threshold
    return papers


def get_low_stock_papers(db: Session):
    papers = db.query(models.Paper).filter(models.Paper.stock_count <= models.Paper.threshold).all()
    for paper in papers:
        paper.is_low_stock = True
    return papers


def create_paper(db: Session, paper: schemas.PaperCreate):
    db_paper = models.Paper(**paper.model_dump())
    db.add(db_paper)
    db.commit()
    db.refresh(db_paper)
    db_paper.is_low_stock = db_paper.stock_count <= db_paper.threshold
    return db_paper


def update_paper(db: Session, paper_id: int, paper_update: schemas.PaperUpdate):
    db_paper = db.query(models.Paper).filter(models.Paper.id == paper_id).first()
    if db_paper:
        update_data = paper_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_paper, key, value)
        db.commit()
        db.refresh(db_paper)
        db_paper.is_low_stock = db_paper.stock_count <= db_paper.threshold
    return db_paper


def delete_paper(db: Session, paper_id: int):
    db_paper = db.query(models.Paper).filter(models.Paper.id == paper_id).first()
    if db_paper:
        db.delete(db_paper)
        db.commit()
        return True
    return False


def get_print_batch(db: Session, batch_id: int):
    return db.query(models.PrintBatch).filter(models.PrintBatch.id == batch_id).first()


def get_print_batches_by_artwork(db: Session, artwork_id: int):
    return db.query(models.PrintBatch).filter(models.PrintBatch.artwork_id == artwork_id).all()


def get_print_batches(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.PrintBatch).order_by(desc(models.PrintBatch.print_date)).offset(skip).limit(limit).all()


def create_print_batch(db: Session, batch: schemas.PrintBatchCreate):
    db_artwork = db.query(models.Artwork).filter(models.Artwork.id == batch.artwork_id).first()
    if not db_artwork:
        raise ValueError("作品不存在")
    
    remaining_edition = db_artwork.planned_edition - db_artwork.sold_count
    if batch.final_print_count > remaining_edition:
        raise ValueError(f"正印数量超过剩余可售版数，剩余: {remaining_edition}")
    
    if batch.paper_id and batch.paper_used > 0:
        db_paper = db.query(models.Paper).filter(models.Paper.id == batch.paper_id).first()
        if not db_paper:
            raise ValueError("纸张不存在")
        if batch.paper_used > db_paper.stock_count:
            raise ValueError(f"纸张库存不足，当前库存: {db_paper.stock_count}")
        db_paper.stock_count -= batch.paper_used
    
    if batch.final_print_count > 0:
        db_artwork.sold_count += batch.final_print_count
    
    db_batch = models.PrintBatch(**batch.model_dump())
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    return db_batch


def delete_print_batch(db: Session, batch_id: int):
    db_batch = db.query(models.PrintBatch).filter(models.PrintBatch.id == batch_id).first()
    if db_batch:
        if db_batch.paper_id and db_batch.paper_used > 0:
            db_paper = db.query(models.Paper).filter(models.Paper.id == db_batch.paper_id).first()
            if db_paper:
                db_paper.stock_count += db_batch.paper_used
        
        if db_batch.final_print_count > 0:
            db_artwork = db.query(models.Artwork).filter(models.Artwork.id == db_batch.artwork_id).first()
            if db_artwork:
                db_artwork.sold_count -= db_batch.final_print_count
        
        db.delete(db_batch)
        db.commit()
        return True
    return False


def get_dashboard_stats(db: Session):
    total_artworks = db.query(func.count(models.Artwork.id)).scalar()
    total_batches = db.query(func.count(models.PrintBatch.id)).scalar()
    total_papers = db.query(func.count(models.Paper.id)).scalar()
    low_stock_count = db.query(func.count(models.Paper.id)).filter(
        models.Paper.stock_count <= models.Paper.threshold
    ).scalar()
    
    return schemas.DashboardStats(
        total_artworks=total_artworks or 0,
        total_batches=total_batches or 0,
        total_papers=total_papers or 0,
        low_stock_count=low_stock_count or 0
    )


def get_print_type_stats(db: Session):
    results = db.query(
        models.Artwork.print_type,
        func.count(models.Artwork.id)
    ).group_by(models.Artwork.print_type).all()
    
    return [
        schemas.PrintTypeStats(name=r[0], value=r[1])
        for r in results
    ]


def get_monthly_batch_stats(db: Session):
    end_date = date.today()
    start_date = end_date - timedelta(days=90)
    
    results = db.query(
        func.strftime('%Y-%m', models.PrintBatch.print_date).label('month'),
        func.count(models.PrintBatch.id)
    ).filter(
        models.PrintBatch.print_date >= start_date
    ).group_by('month').order_by('month').all()
    
    return [
        schemas.MonthlyBatchStats(month=r[0], count=r[1])
        for r in results
    ]


def get_waste_rate_stats(db: Session):
    results = db.query(
        models.Artwork.name,
        func.sum(models.PrintBatch.waste_count).label('waste'),
        func.sum(models.PrintBatch.trial_print_count + models.PrintBatch.final_print_count + models.PrintBatch.waste_count).label('total')
    ).join(
        models.PrintBatch, models.Artwork.id == models.PrintBatch.artwork_id
    ).group_by(models.Artwork.id).having(
        func.sum(models.PrintBatch.waste_count) > 0
    ).order_by(desc('waste')).limit(10).all()
    
    return [
        schemas.WasteRateStats(
            artwork_name=r[0],
            waste_rate=round((r[1] / r[2] * 100) if r[2] > 0 else 0, 2)
        )
        for r in results
    ]

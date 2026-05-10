from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ArtworkBase(BaseModel):
    name: str
    print_type: str
    finished_size: Optional[str] = None
    planned_edition: int
    signature_rule: Optional[str] = None

class ArtworkCreate(ArtworkBase):
    pass

class ArtworkUpdate(BaseModel):
    name: Optional[str] = None
    print_type: Optional[str] = None
    finished_size: Optional[str] = None
    planned_edition: Optional[int] = None
    signature_rule: Optional[str] = None

class Artwork(ArtworkBase):
    id: int
    created_at: datetime
    sold_edition: Optional[int] = 0
    remaining_edition: Optional[int] = 0

    class Config:
        orm_mode = True

class PlateBase(BaseModel):
    artwork_id: int
    color_number: int
    ink_ratio: Optional[str] = None
    is_finalized: bool = False

class PlateCreate(PlateBase):
    pass

class PlateUpdate(BaseModel):
    color_number: Optional[int] = None
    ink_ratio: Optional[str] = None
    is_finalized: Optional[bool] = None

class Plate(PlateBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class PaperBase(BaseModel):
    name: str
    weight: Optional[int] = None
    size: Optional[str] = None
    stock: int = 0
    cost_per_sheet: float = 0
    threshold: int = 50

class PaperCreate(PaperBase):
    pass

class PaperUpdate(BaseModel):
    name: Optional[str] = None
    weight: Optional[int] = None
    size: Optional[str] = None
    stock: Optional[int] = None
    cost_per_sheet: Optional[float] = None
    threshold: Optional[int] = None

class Paper(PaperBase):
    id: int
    created_at: datetime
    is_low_stock: Optional[bool] = False

    class Config:
        orm_mode = True

class BatchPlateBase(BaseModel):
    plate_id: int

class BatchPlateCreate(BatchPlateBase):
    pass

class BatchPlate(BatchPlateBase):
    id: int

    class Config:
        orm_mode = True

class PrintBatchBase(BaseModel):
    artwork_id: int
    print_date: datetime
    test_prints: int = 0
    good_prints: int = 0
    waste_prints: int = 0
    paper_id: Optional[int] = None
    paper_used: int = 0
    notes: Optional[str] = None

class PrintBatchCreate(PrintBatchBase):
    plates: List[int] = []

class PrintBatchUpdate(BaseModel):
    artwork_id: Optional[int] = None
    print_date: Optional[datetime] = None
    test_prints: Optional[int] = None
    good_prints: Optional[int] = None
    waste_prints: Optional[int] = None
    paper_id: Optional[int] = None
    paper_used: Optional[int] = None
    notes: Optional[str] = None
    plates: Optional[List[int]] = None

class PrintBatch(PrintBatchBase):
    id: int
    created_at: datetime
    plates: List[Plate] = []

    class Config:
        orm_mode = True

class DashboardStats(BaseModel):
    total_artworks: int
    total_batches: int
    total_papers: int
    low_stock_count: int

class ArtworkStats(BaseModel):
    id: int
    name: str
    print_type: str
    planned_edition: int
    total_good_prints: int
    remaining_edition: int

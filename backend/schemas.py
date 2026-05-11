from pydantic import BaseModel
from datetime import date
from typing import Optional, List


class ArtworkBase(BaseModel):
    name: str
    print_type: str
    finished_size: Optional[str] = None
    planned_edition: int
    signature_rule: Optional[str] = None


class ArtworkCreate(ArtworkBase):
    pass


class Artwork(ArtworkBase):
    id: int
    sold_count: int
    remaining_edition: int

    class Config:
        from_attributes = True


class PlateBase(BaseModel):
    artwork_id: int
    color_number: int
    ink_ratio: Optional[str] = None
    is_finalized: bool = False
    notes: Optional[str] = None


class PlateCreate(PlateBase):
    pass


class PlateUpdate(BaseModel):
    color_number: Optional[int] = None
    ink_ratio: Optional[str] = None
    is_finalized: Optional[bool] = None
    notes: Optional[str] = None


class Plate(PlateBase):
    id: int

    class Config:
        from_attributes = True


class PaperBase(BaseModel):
    name: str
    weight: Optional[int] = None
    size: Optional[str] = None
    stock_count: int = 0
    cost_per_sheet: Optional[float] = None
    threshold: int = 50


class PaperCreate(PaperBase):
    pass


class PaperUpdate(BaseModel):
    name: Optional[str] = None
    weight: Optional[int] = None
    size: Optional[str] = None
    stock_count: Optional[int] = None
    cost_per_sheet: Optional[float] = None
    threshold: Optional[int] = None


class Paper(PaperBase):
    id: int
    is_low_stock: bool

    class Config:
        from_attributes = True


class PrintBatchBase(BaseModel):
    artwork_id: int
    print_date: date
    plate_ids: Optional[str] = None
    trial_print_count: int = 0
    final_print_count: int = 0
    waste_count: int = 0
    paper_id: Optional[int] = None
    paper_used: int = 0
    notes: Optional[str] = None


class PrintBatchCreate(PrintBatchBase):
    pass


class PrintBatch(PrintBatchBase):
    id: int

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_artworks: int
    total_batches: int
    total_papers: int
    low_stock_count: int


class PrintTypeStats(BaseModel):
    name: str
    value: int


class MonthlyBatchStats(BaseModel):
    month: str
    count: int


class WasteRateStats(BaseModel):
    artwork_name: str
    waste_rate: float

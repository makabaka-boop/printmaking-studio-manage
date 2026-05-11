from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from database import Base


class Artwork(Base):
    __tablename__ = "artworks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    print_type = Column(String(50), nullable=False)
    finished_size = Column(String(100))
    planned_edition = Column(Integer, nullable=False)
    signature_rule = Column(Text)
    sold_count = Column(Integer, default=0)
    created_at = Column(Date)

    plates = relationship("Plate", back_populates="artwork")
    batches = relationship("PrintBatch", back_populates="artwork")


class Plate(Base):
    __tablename__ = "plates"

    id = Column(Integer, primary_key=True, index=True)
    artwork_id = Column(Integer, ForeignKey("artworks.id"), nullable=False)
    color_number = Column(Integer, nullable=False)
    ink_ratio = Column(Text)
    is_finalized = Column(Boolean, default=False)
    notes = Column(Text)

    artwork = relationship("Artwork", back_populates="plates")


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    weight = Column(Integer)
    size = Column(String(100))
    stock_count = Column(Integer, default=0)
    cost_per_sheet = Column(Float)
    threshold = Column(Integer, default=50)


class PrintBatch(Base):
    __tablename__ = "print_batches"

    id = Column(Integer, primary_key=True, index=True)
    artwork_id = Column(Integer, ForeignKey("artworks.id"), nullable=False)
    print_date = Column(Date, nullable=False)
    plate_ids = Column(String(500))
    trial_print_count = Column(Integer, default=0)
    final_print_count = Column(Integer, default=0)
    waste_count = Column(Integer, default=0)
    paper_id = Column(Integer, ForeignKey("papers.id"))
    paper_used = Column(Integer, default=0)
    notes = Column(Text)

    artwork = relationship("Artwork", back_populates="batches")

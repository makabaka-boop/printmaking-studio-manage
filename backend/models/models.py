from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database.database import Base

class Artwork(Base):
    __tablename__ = "artworks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    print_type = Column(String(50), nullable=False)
    finished_size = Column(String(100))
    planned_edition = Column(Integer, nullable=False)
    signature_rule = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    plates = relationship("Plate", back_populates="artwork", cascade="all, delete-orphan")
    batches = relationship("PrintBatch", back_populates="artwork", cascade="all, delete-orphan")

class Plate(Base):
    __tablename__ = "plates"

    id = Column(Integer, primary_key=True, index=True)
    artwork_id = Column(Integer, ForeignKey("artworks.id"), nullable=False)
    color_number = Column(Integer, nullable=False)
    ink_ratio = Column(Text)
    is_finalized = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    artwork = relationship("Artwork", back_populates="plates")
    print_batches = relationship("BatchPlate", back_populates="plate")

class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    weight = Column(Integer)
    size = Column(String(100))
    stock = Column(Integer, default=0)
    cost_per_sheet = Column(Float, default=0)
    threshold = Column(Integer, default=50)
    created_at = Column(DateTime, default=datetime.utcnow)

class PrintBatch(Base):
    __tablename__ = "print_batches"

    id = Column(Integer, primary_key=True, index=True)
    artwork_id = Column(Integer, ForeignKey("artworks.id"), nullable=False)
    print_date = Column(DateTime, default=datetime.utcnow)
    test_prints = Column(Integer, default=0)
    good_prints = Column(Integer, default=0)
    waste_prints = Column(Integer, default=0)
    paper_id = Column(Integer, ForeignKey("papers.id"))
    paper_used = Column(Integer, default=0)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    artwork = relationship("Artwork", back_populates="batches")
    paper = relationship("Paper")
    plates_used = relationship("BatchPlate", back_populates="batch", cascade="all, delete-orphan")

class BatchPlate(Base):
    __tablename__ = "batch_plates"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("print_batches.id"), nullable=False)
    plate_id = Column(Integer, ForeignKey("plates.id"), nullable=False)

    batch = relationship("PrintBatch", back_populates="plates_used")
    plate = relationship("Plate", back_populates="print_batches")

from sqlalchemy import Column, Integer, String, LargeBinary
from database import Base
from datetime import datetime
from sqlalchemy import DateTime
class Image(Base):
    __tablename__ = 'images'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    content_type = Column(String(50))
    data = Column(LargeBinary)  # For storing binary image data
    created_at = Column(DateTime, default=datetime.utcnow)
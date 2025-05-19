from sqlalchemy import Column, Integer, String, LargeBinary, DateTime
from database import Base
from datetime import datetime

class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    content_type = Column(String(50))
    data = Column(LargeBinary)
    created_at = Column(DateTime, default=datetime.utcnow)
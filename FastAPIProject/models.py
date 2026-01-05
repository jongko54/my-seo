from sqlalchemy import Column, Integer, String, Text, DateTime
from database import Base
import datetime

class Market(Base):
    __tablename__ = "market"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    content = Column(Text)
    price = Column(Integer)
    image_url = Column(String(500))
    url_keyword = Column(String(255), unique=True)
    create_date = Column(DateTime, default=datetime.datetime.now)
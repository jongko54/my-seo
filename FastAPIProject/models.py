from sqlalchemy import Column, Integer, String, Text, DateTime
from database import Base
import datetime

class Market(Base):
    __tablename__ = "market"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)   # 여기가 name 이어야 함! (title 아님)
    content = Column(Text)                       # 여기가 content 이어야 함!
    price = Column(Integer)
    image_url = Column(String(500))
    create_date = Column(DateTime, default=datetime.datetime.now)
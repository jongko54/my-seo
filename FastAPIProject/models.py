from sqlalchemy import Column, Integer, String, Text
from database import Base


class Market(Base):
    __tablename__ = "market"

    id = Column(Integer, primary_key=True, index=True)
    url_keyword = Column(String(100), unique=True, index=True)  # 예: rose

    # --- [추가된 정보] ---
    store_name = Column(String(100), default="bnt 식물원")  # 가게 이름
    account_number = Column(String(100))  # 계좌번호 (문자열 추천: 하이픈 포함)
    price = Column(String(50))  # 가격 (예: "30,000원" 또는 숫자)
    # -------------------

    title = Column(String(200))
    description = Column(String(300))
    content = Column(Text)
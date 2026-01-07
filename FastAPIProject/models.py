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


class Order(Base):
    __tablename__ = "orders"

    # 1. 관리용 번호 (DB 내부용)
    id = Column(Integer, primary_key=True, index=True)

    # 2. 토스페이먼츠 연동 필수 정보
    # order_uid: 토스에 보낼 주문번호 (예: 20240501-A1B2C3...) - 중복되면 안 됨!
    order_uid = Column(String(255), unique=True, nullable=False)
    # item_name: 상품명 스냅샷 (예: "장미 꽃다발 외 1건")
    item_name = Column(String(255), nullable=False)
    # payment_key: 결제 성공 후 토스에서 주는 영수증 키 (환불할 때 필요)
    payment_key = Column(String(255), nullable=True)

    # 3. 결제 금액 및 상태
    amount = Column(Integer, nullable=False)
    status = Column(String(50), default="READY")  # READY(대기), PAID(완료), CANCELED(취소)

    # 4. 보내는 분 (주문자) - 비회원 결제이므로 여기에 직접 저장
    buyer_name = Column(String(100), nullable=False)
    buyer_phone = Column(String(50), nullable=False)

    # 5. 받는 분 (배송지)
    receiver_name = Column(String(100), nullable=False)
    receiver_phone = Column(String(50), nullable=False)
    address = Column(Text, nullable=False)
    message = Column(Text, nullable=True)  # 꽃바구니 리본 문구 or 카드 메시지

    # 6. 주문 시각
    create_date = Column(DateTime, default=datetime.datetime.now)
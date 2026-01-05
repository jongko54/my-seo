import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 1. 환경변수 가져오기 (없으면 기본값 사용)
user = os.getenv("MYSQLUSER", "root")
password = os.getenv("MYSQLPASSWORD", "")
host = os.getenv("MYSQLHOST", "localhost")
port = os.getenv("MYSQLPORT", "3306")
db_name = os.getenv("MYSQLDATABASE", "railway")

# 2. DB URL 만들기 (SQLAlchemy용)
# 중요: mysql-connector-python을 설치했다면 'mysql+mysqlconnector://'를 써야 합니다.
DATABASE_URL = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db_name}"

# 3. 엔진 생성
# (여기서 URL이 제대로 안 만들어지면 아까 그 'got None' 에러가 납니다)
if not password:
    print("경고: 비밀번호가 없습니다. 환경변수를 확인하세요!")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
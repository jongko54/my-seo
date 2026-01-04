import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# .env 파일 로드 (로컬 개발용)
load_dotenv()

# Railway에서 제공하는 URL 가져오기
DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy는 'mysql://' 대신 'mysql+pymysql://'이 필요합니다.
if DATABASE_URL and DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://")

# DB 엔진 생성
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# DB 세션 의존성 함수 (나중에 main.py에서 씀)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
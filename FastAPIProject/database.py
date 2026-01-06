import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# ========================================================
# 1. 환경변수 설정 (수정된 부분)
# Railway에 등록한 'DATABASE_URL' 변수를 가장 먼저 찾습니다.
# ========================================================
DATABASE_URL = os.getenv("DATABASE_URL")

# 만약 Railway 변수가 없으면(내 컴퓨터에서 실행할 때), 기존 방식대로 하나씩 조립합니다.
if not DATABASE_URL:
    user = os.getenv("MYSQLUSER", "root")
    password = os.getenv("MYSQLPASSWORD", "")
    host = os.getenv("MYSQLHOST", "localhost")
    port = os.getenv("MYSQLPORT", "3306")
    db_name = os.getenv("MYSQLDATABASE", "railway")

    DATABASE_URL = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db_name}"

# ★ 중요: Railway가 주는 주소는 보통 'mysql://'로 시작하는데,
# mysql-connector를 쓴다면 'mysql+mysqlconnector://'로 바꿔줘야 에러가 안 납니다.
if DATABASE_URL and DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+mysqlconnector://")

# ========================================================
# 2. 엔진 생성
# ========================================================
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# main.py
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Response
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
import pandas as pd
import io
from datetime import datetime
from database import get_db, Place, engine
from fastapi.templating import Jinja2Templates
from fastapi import Request

app = FastAPI(title="맛집/술집 추천 SEO API")
templates = Jinja2Templates(directory="templates")


# --- 1. 엑셀/CSV 데이터 연동 (업로드) ---

@app.post("/upload-data/")
async def upload_places(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    엑셀(.xlsx) 또는 CSV 파일을 업로드하여 DB에 저장합니다.
    컬럼명: name, category, address, description
    """

    # 1. 파일 확장자 확인 및 데이터프레임 변환
    contents = await file.read()
    if file.filename.endswith('.csv'):
        # 한글 깨짐 방지를 위해 encoding='utf-8-sig' 권장
        df = pd.read_csv(io.BytesIO(contents), encoding='utf-8-sig')
    elif file.filename.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(io.BytesIO(contents))
    else:
        raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식입니다.")

    # 2. 데이터 유효성 검사 및 DB 저장 (Bulk Insert)
    # 실제로는 중복 체크 로직 등이 필요할 수 있습니다.
    places_to_add = []
    for _, row in df.iterrows():
        place = Place(
            name=row['name'],
            category=row['category'],
            address=row['address'],
            description=row.get('description', '')  # 설명이 없으면 빈 값
        )
        places_to_add.append(place)

    try:
        db.add_all(places_to_add)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"데이터 저장 중 오류 발생: {str(e)}")

    return {"message": f"성공적으로 {len(places_to_add)}개의 맛집/술집 데이터를 등록했습니다."}


# --- 2. 사이트맵 자동 생성 (SEO) ---

@app.get("/sitemap.xml", response_class=Response)
def generate_sitemap(db: Session = Depends(get_db)):
    """
    구글 봇이 크롤링할 수 있도록 sitemap.xml을 동적으로 생성합니다.
    모든 맛집/술집의 상세 페이지 URL을 반환합니다.
    """
    places = db.query(Place).all()
    base_url = "bntflower.co.kr"  # 실제 운영 도메인으로 변경 필수

    # XML 헤더
    xml_content = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    # 1. 정적 페이지 (메인 등)
    xml_content.append(f"""
    <url>
        <loc>{base_url}/</loc>
        <lastmod>{datetime.utcnow().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    """)

    # 2. 동적 페이지 (DB에 있는 맛집들)
    for place in places:
        # URL 구조: /place/{id} 라고 가정
        # lastmod: 구글에게 콘텐츠가 언제 수정되었는지 알려줌
        last_mod = place.updated_at.strftime('%Y-%m-%d') if place.updated_at else datetime.utcnow().strftime('%Y-%m-%d')

        xml_content.append(f"""
        <url>
            <loc>{base_url}/place/{place.id}</loc>
            <lastmod>{last_mod}</lastmod>
            <changefreq>weekly</changefreq>
            <priority>0.8</priority>
        </url>
        """)

    xml_content.append('</urlset>')

    return Response(content="".join(xml_content), media_type="application/xml")


# --- 3. Robots.txt (구글 봇 안내) ---

@app.get("/robots.txt", response_class=PlainTextResponse)
def robots_txt():
    """
    검색 엔진 봇에게 sitemap 위치를 알려줍니다.
    """
    base_url = "bntflower.co.kr"  # 실제 도메인
    content = f"""User-agent: *
Allow: /
Sitemap: {base_url}/sitemap.xml
"""
    return content


# --- [추가] 상세 페이지 라우터 (실제 화면) ---
@app.get("/place/{place_id}")
def read_place(request: Request, place_id: int, db: Session = Depends(get_db)):
    # DB에서 해당 ID의 맛집 찾기
    place = db.query(Place).filter(Place.id == place_id).first()

    if not place:
        raise HTTPException(status_code=404, detail="맛집을 찾을 수 없습니다.")

    # HTML 파일에 데이터 채워서 보내주기
    return
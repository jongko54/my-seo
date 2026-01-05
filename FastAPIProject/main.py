from fastapi import FastAPI, Depends, Request, HTTPException, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import models
from database import engine, get_db

# 1. DB 테이블 자동 생성 (테이블이 없으면 만듭니다)
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 도메인 주소 (나중에 사이트맵 만들 때 씀)
DOMAIN = "https://bntflower.co.kr"


# ==========================
# 1. 홈 페이지
# ==========================
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    # 최신 데이터 10개만 가져와서 링크 보여주기
    items = db.query(models.Market).limit(50).all()

    return templates.TemplateResponse("index_list.html", {
        "request": request,
        "items": items
    })
    # 주의: templates 폴더에 index_list.html도 간단히 하나 만들어주세요.
    # (없으면 에러나니 아래 item.html과 비슷하게 만드시면 됩니다)


# ==========================
# 2. SEO 상세 페이지 (pSEO 핵심)
# 주소 예시: https://bntflower.co.kr/market/rose
# ==========================
@app.get("/market/{keyword}", response_class=HTMLResponse)
def read_item(request: Request, keyword: str, db: Session = Depends(get_db)):
    # DB에서 keyword로 검색
    item = db.query(models.Market).filter(models.Market.url_keyword == keyword).first()

    if not item:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")

    return templates.TemplateResponse("item.html", {"request": request, "item": item})


# ==========================
# 3. 사이트맵 자동 생성 (구글 제출용)
# ==========================
@app.get("/sitemap.xml")
def sitemap(db: Session = Depends(get_db)):
    items = db.query(models.Market).all()

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    # 홈 추가
    xml += f'<url><loc>{DOMAIN}/</loc></url>\n'

    # DB에 있는 모든 페이지 추가
    for item in items:
        loc = f"{DOMAIN}/market/{item.url_keyword}"
        xml += f'<url><loc>{loc}</loc></url>\n'

    xml += '</urlset>'
    return Response(content=xml, media_type="application/xml")


# ==========================
# 4. Robots.txt
# ==========================
@app.get("/robots.txt")
def robots():
    content = f"""User-agent: *
Allow: /
Sitemap: {DOMAIN}/sitemap.xml
"""
    return Response(content=content, media_type="text/plain")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
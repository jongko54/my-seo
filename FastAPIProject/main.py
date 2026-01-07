from fastapi import FastAPI, Depends, Request, HTTPException, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import models
from database import engine, get_db

# 1. DB 테이블 자동 생성
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 도메인 설정
DOMAIN = "https://bntflower.co.kr"


# ==========================
# 1. 홈 페이지 (메인)
# ==========================
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    # DB에서 아이템을 가져오지만, 아까 만든 index_list.html은 정적 링크를 쓰므로
    # items 변수는 나중에 필요할 때 html에서 {{ items }}로 쓰시면 됩니다.
    items = db.query(models.Market).limit(50).all()

    return templates.TemplateResponse("index_list.html", {
        "request": request,
        "items": items
    })


# ==========================
# [추가됨] 2. 실제 주문/계산기 페이지
# 아까 만든 item.html (화환/난 가격 계산 기능)을 보여주는 곳입니다.
# ==========================
@app.get("/item", response_class=HTMLResponse)
def read_order_page(request: Request):
    """
    사용자가 메인에서 '화환', '난' 등을 클릭했을 때 도착하는 페이지.
    URL 파라미터(?category=화환)는 item.html 내부의 자바스크립트가 처리합니다.
    """
    return templates.TemplateResponse("item.html", {"request": request})


# ==========================
# 3. SEO 상세 페이지 (pSEO - 기존 유지)
# 검색엔진 유입용 (예: /market/강남구꽃배달)
# ==========================
@app.get("/market/{keyword}", response_class=HTMLResponse)
def read_seo_item(request: Request, keyword: str, db: Session = Depends(get_db)):
    # DB에서 keyword로 검색
    item = db.query(models.Market).filter(models.Market.url_keyword == keyword).first()

    if not item:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")

    # 주의: 여기서도 item.html을 쓸지, 별도의 seo_template.html을 쓸지 결정해야 합니다.
    # 일단은 item 객체를 넘겨주는 형태로 유지합니다.
    return templates.TemplateResponse("item.html", {"request": request, "item": item})


# ==========================
# 4. 사이트맵 (구글 제출용)
# ==========================
@app.get("/sitemap.xml")
def sitemap(db: Session = Depends(get_db)):
    items = db.query(models.Market).all()

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    # 1) 메인 페이지
    xml += f'<url><loc>{DOMAIN}/</loc></url>\n'

    # 2) 주문 페이지들 (주요 카테고리 고정)
    categories = ["화환", "난", "꽃다발", "탁상용", "사무실"]
    for cat in categories:
        xml += f'<url><loc>{DOMAIN}/item?category={cat}</loc></url>\n'

    # 3) DB에 있는 pSEO 페이지들
    for item in items:
        # url_keyword가 한글일 경우 URL 인코딩이 필요할 수 있습니다.
        loc = f"{DOMAIN}/market/{item.url_keyword}"
        xml += f'<url><loc>{loc}</loc></url>\n'

    xml += '</urlset>'
    return Response(content=xml, media_type="application/xml")


# ==========================
# 5. Robots.txt
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

    # Railway 등 배포 환경을 위해 host는 0.0.0.0으로 설정
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
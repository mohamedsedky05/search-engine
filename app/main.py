"""
FastAPI application: search API, health, status, and optional crawl/index triggers.
"""
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import (
    CRAWLER_MAX_DEPTH,
    CRAWLER_MAX_PAGES,
    CRAWLER_SEED_URLS,
    SEARCH_RESULTS_PER_PAGE,
)
from app.database import (
    get_document_count,
    get_index_terms_count,
    get_last_crawl_stats,
    init_db,
)
from app.schemas import (
    BuildIndexResponse,
    CrawlRequest,
    CrawlResponse,
    SearchRequest,
    SearchResponse,
    SearchResultItem,
    StatusResponse,
)
from app.search import SearchService
from app.crawler import Crawler
from app.indexing import Indexer

app = FastAPI(
    title="Mini Search Engine",
    description="Web crawler and TF-IDF search engine API",
    version="1.0.0",
)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Mount static files if directory exists
static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

search_service = SearchService()


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/status", response_model=StatusResponse)
def status() -> StatusResponse:
    docs = get_document_count()
    terms = get_index_terms_count()
    last_crawl = get_last_crawl_stats()
    return StatusResponse(
        status="ok",
        documents_count=docs,
        index_terms_count=terms,
        last_crawl_pages=last_crawl[0] if last_crawl else None,
        last_crawl_errors=last_crawl[1] if last_crawl else None,
    )


@app.get("/", response_class=HTMLResponse)
def index_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/search", response_class=HTMLResponse)
def search_page(
    request: Request,
    q: str = Query("", min_length=0),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
) -> HTMLResponse:
    results = []
    total = 0
    if q.strip():
        results, total = search_service.search(q.strip(), page=page, per_page=per_page)
    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "query": q,
            "results": results,
            "total": total,
            "page": page,
            "per_page": per_page,
        },
    )


@app.post("/api/search", response_model=SearchResponse)
def api_search(body: SearchRequest) -> SearchResponse:
    results, total = search_service.search(
        body.q, page=body.page, per_page=body.per_page
    )
    return SearchResponse(
        query=body.q,
        total=total,
        page=body.page,
        per_page=body.per_page,
        results=[
            SearchResultItem(
                url=r.url,
                title=r.title,
                snippet=r.snippet,
                score=r.score,
            )
            for r in results
        ],
    )


@app.post("/api/crawl", response_model=CrawlResponse)
def api_crawl(body: Optional[CrawlRequest] = None) -> CrawlResponse:
    seed_urls = (body and body.seed_urls) or CRAWLER_SEED_URLS
    max_pages = (body and body.max_pages) or CRAWLER_MAX_PAGES
    max_depth = (body and body.max_depth) or CRAWLER_MAX_DEPTH
    crawler = Crawler(seed_urls=seed_urls, max_pages=max_pages, max_depth=max_depth)
    pages_crawled, urls_discovered, errors = crawler.run()
    return CrawlResponse(
        message="Crawl completed",
        pages_crawled=pages_crawled,
        urls_discovered=urls_discovered,
        errors=errors,
    )


@app.post("/api/build-index", response_model=BuildIndexResponse)
def api_build_index() -> BuildIndexResponse:
    indexer = Indexer()
    docs_count, terms_count = indexer.build()
    return BuildIndexResponse(
        message="Index built successfully",
        documents_indexed=docs_count,
        terms_count=terms_count,
    )


if __name__ == "__main__":
    import uvicorn
    from app.config import HOST, PORT
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)

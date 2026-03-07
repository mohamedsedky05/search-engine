"""
Pydantic schemas for API request/response models.
"""
from typing import List, Optional

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Request body for search API."""
    q: str = Field(..., min_length=1, description="Search query")
    page: int = Field(1, ge=1, description="Page number for pagination")
    per_page: int = Field(10, ge=1, le=50, description="Results per page")


class SearchResultItem(BaseModel):
    """Single result item in API response."""
    url: str
    title: str
    snippet: str
    score: float


class SearchResponse(BaseModel):
    """Response for search API."""
    query: str
    total: int
    page: int
    per_page: int
    results: List[SearchResultItem]


class CrawlRequest(BaseModel):
    """Request to start a crawl (optional body)."""
    seed_urls: Optional[List[str]] = None
    max_pages: Optional[int] = None
    max_depth: Optional[int] = None


class CrawlResponse(BaseModel):
    """Response after crawl run."""
    message: str
    pages_crawled: int
    urls_discovered: int
    errors: int


class BuildIndexResponse(BaseModel):
    """Response after index build."""
    message: str
    documents_indexed: int
    terms_count: int


class StatusResponse(BaseModel):
    """API status and crawl/index statistics."""
    status: str = "ok"
    documents_count: int = 0
    index_terms_count: int = 0
    last_crawl_pages: Optional[int] = None
    last_crawl_errors: Optional[int] = None

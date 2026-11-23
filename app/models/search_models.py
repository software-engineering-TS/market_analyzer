"""
Search Models
"""

from pydantic import BaseModel


class SearchStock(BaseModel):
    symbol: str
    company_name: str
    exchange: str
    series: str | None = None


class SearchResponse(BaseModel):
    stocks: list[SearchStock]
    total: int
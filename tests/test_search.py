from app.services.search_service import SearchService


class FakeSearchRepository:
    def search_stocks(self, query, limit=10, offset=0):
        return [
            {
                "symbol": "TCS",
                "company_name": "TATA CONSULTANCY SERVICES",
                "exchange": "NSE",
                "series": None,
            }
        ]


def test_search_accepts_stock_without_series():
    service = SearchService(FakeSearchRepository())

    result = service.search_stocks("TCS")

    assert result.total == 1
    assert result.stocks[0].symbol == "TCS"
    assert result.stocks[0].series is None

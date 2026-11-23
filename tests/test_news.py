"""News provider behavior tests."""

from app.providers.news_provider import NewsProvider


def test_news_provider_returns_none_when_external_provider_fails(monkeypatch):
    class BrokenTicker:
        @property
        def news(self):
            raise RuntimeError("upstream unavailable")

    class FakeYFinance:
        @staticmethod
        def Ticker(symbol):
            return BrokenTicker()

    monkeypatch.setattr("app.providers.news_provider.yf", FakeYFinance)
    assert NewsProvider().get_news("TCS.NS") is None


def test_news_provider_returns_none_for_empty_news(monkeypatch):
    class EmptyTicker:
        news = []

    class FakeYFinance:
        @staticmethod
        def Ticker(symbol):
            return EmptyTicker()

    monkeypatch.setattr("app.providers.news_provider.yf", FakeYFinance)
    assert NewsProvider().get_news("TCS.NS") is None

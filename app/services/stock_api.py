import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Any


class StockAPIService:
    """
    Stock data retrieval service using yfinance
    Handles real-time and historical stock data
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_stock_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive stock information

        Args:
        symbol (str): Ticker symbol (e.g., 'AAPL')

        Returns:
        dict: Stock information or None if error
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Validate that we got real data
            if not info or info.get("regularMarketPrice") is None:
                self.logger.warning(f"No data found for symbol: {symbol}")
                return None

            return {
                "symbol": symbol.upper(),
                "company_name": info.get("longName", symbol),
                "current_price": info.get("regularMarketPrice"),
                "previous_close": info.get("previousClose"),
                "open_price": info.get("regularMarketOpen"),
                "day_high": info.get("dayHigh"),
                "day_low": info.get("dayLow"),
                "volume": info.get("regularMarketVolume"),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "dividend_yield": info.get("dividendYield"),
                "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
                "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "exchange": info.get("exchange"),
                "currency": info.get("currency", "USD"),
                "country": info.get("country", "US"),
                "last_updated": datetime.now(),
            }

        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {e}")
            return None

    def get_historical_data(
        self, symbol: str, period: str = "1mo"
    ) -> Optional[List[Dict]]:
        """
        Get historical price data

        Args:
        symbol (str): Ticker symbol
        period (str): Period ("1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max")

        Returns:
        list: Historical data or None if error
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)

            if hist.empty:
                self.logger.warning(f"No historical data found for symbol: {symbol}")
                return None

            # Convert to list of dictionaries
            historical_data = []
            for date, row in hist.iterrows():
                historical_data.append(
                    {
                        "date": date.date(),
                        "open": round(row["Open"], 2),
                        "high": round(row["High"], 2),
                        "low": round(row["Low"], 2),
                        "close": round(row["Close"], 2),
                        "volume": (
                            int(row["Volume"]) if not pd.isna(row["Volume"]) else 0
                        ),
                    }
                )

            return historical_data

        except Exception as e:
            self.logger.error(f"Error fetching historical data for {symbol}: {e}")
            return None

    def search_stocks(self, query: str) -> List[Dict[str, str]]:
        """
        Search for stocks by name or symbol

        Args:
            query (str): Search query

        Returns:
            list: List of matching stocks
        """
        # This is a basic implementation
        # In production, you might want to use a dedicated search API

        # Common stock symbols for demo
        common_stocks = [
            {"symbol": "AAPL", "name": "Apple Inc."},
            {"symbol": "GOOGL", "name": "Alphabet Inc."},
            {"symbol": "MSFT", "name": "Microsoft Corporation"},
            {"symbol": "AMZN", "name": "Amazon.com Inc."},
            {"symbol": "TSLA", "name": "Tesla Inc."},
            {"symbol": "NVDA", "name": "NVIDIA Corporation"},
            {"symbol": "META", "name": "Meta Platforms Inc."},
            {"symbol": "NFLX", "name": "Netflix Inc."},
            {"symbol": "AMD", "name": "Advanced Micro Devices"},
            {"symbol": "INTC", "name": "Intel Corporation"},
        ]

        query_lower = query.lower()
        results = []

        for stock in common_stocks:
            if (
                query_lower in stock["symbol"].lower()
                or query_lower in stock["name"].lower()
            ):
                results.append(stock)

        return results[:10]

    def validate_symbol(self, symbol: str) -> bool:
        """
        Validate if a stock symbol exists

        Args:
        symbol (str): Ticker symbol

        Returns:
        bool: True if valid symbol
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return info and info.get("regularMarketPrice") is not None
        except:
            return False

    def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Get current quotes for multiple symbols

        Args:
        symbols (list): List of ticker symbols

        Returns:
        dict: Dictionary with symbol as key and quote data as value
        """
        results = {}

        for symbol in symbols:
            quote_data = self.get_stock_info(symbol)
            if quote_data:
                results[symbol] = quote_data

        return results

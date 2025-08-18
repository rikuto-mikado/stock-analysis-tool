from app.models import db, BaseModel
from sqlalchemy import Index, func
from datetime import datetime, timedelta


class PriceHistory(BaseModel):
    """
    Stock price history model
    Manages historical stock price data
    """

    __tablename__ = "price_history"

    # Foreign key
    stock_id = db.Column(db.Integer, db.ForeignKey("stocks.id"), nullable=False)

    # Date and time
    date = db.Column(db.Date, nullable=False, index=True)
    timestamp = db.Column(db.DateTime, nullable=False, index=True)

    # Price data
    open_price = db.Column(db.Float, nullable=False)
    high_price = db.Column(db.Float, nullable=False)
    low_price = db.Column(db.Float, nullable=False)
    close_price = db.Column(db.Float, nullable=False)
    adjusted_close = db.Column(db.Float, nullable=True)

    # Volume data
    volume = db.Column(db.BigInteger, nullable=True)

    # Technical indicators (optional)
    sma_20 = db.Column(db.Float, nullable=True)
    sma_50 = db.Column(db.Float, nullable=True)
    rsi = db.Column(db.Float, nullable=True)

    # Metadata
    data_source = db.Column(db.String(50), default="yfinance", nullable=False)

    # Index settings for performance
    __table_args__ = (
        Index("idx_stock_date", "stock_id", "date"),
        Index("idx_stock_timestamp", "stock_id", "timestamp"),
        Index("idx_date_range", "date"),
        # Unique constraint to prevent duplicate data
        db.UniqueConstraint(
            "stock_id", "date", "timestamp", name="unique_stock_datetime"
        ),
    )

    def __init__(
        self, stock_id, date, open_price, high_price, low_price, close_price, **kwargs
    ):
        """
        Constructor

        Args:
            stock_id (int): Stock ID
            date (date): Trading date
            open_price (float): Opening price
            high_price (float): High price
            low_price (float): Low price
            close_price (float): Closing price
            **kwargs: Other parameters
        """
        super().__init__()
        self.stock_id = stock_id
        self.date = date
        self.open_price = open_price
        self.high_price = high_price
        self.low_price = low_price
        self.close_price = close_price

        # Set timestamp if not provided
        if "timestamp" not in kwargs:
            self.timestamp = datetime.combine(date, datetime.min.time())

        # Set optional arguments
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @classmethod
    def get_latest_price(cls, stock_id):
        """
        Get the latest price data for a stock

        Args:
            stock_id (int): Stock ID

        Returns:
            PriceHistory: Latest price data, None if not found
        """
        return (
            cls.query.filter_by(stock_id=stock_id)
            .order_by(cls.date.desc(), cls.timestamp.desc())
            .first()
        )

    @classmethod
    def get_price_range(cls, stock_id, start_date, end_date=None):
        """
        Get price data within a date range

        Args:
            stock_id (int): Stock ID
            start_date (date): Start date
            end_date (date): End date (default: today)

        Returns:
            list: List of price history within the range
        """
        if end_date is None:
            end_date = datetime.now().date()

        return (
            cls.query.filter(
                cls.stock_id == stock_id, cls.date >= start_date, cls.date <= end_date
            )
            .order_by(cls.date.asc())
            .all()
        )

    @classmethod
    def get_recent_prices(cls, stock_id, days=30):
        """
        Get recent price data

        Args:
            stock_id (int): Stock ID
            days (int): Number of recent days

        Returns:
            list: List of recent price history
        """
        start_date = datetime.now().date() - timedelta(days=days)
        return cls.get_price_range(stock_id, start_date)

    @classmethod
    def get_monthly_data(cls, stock_id, year, month):
        """
        Get price data for a specific month

        Args:
            stock_id (int): Stock ID
            year (int): Year
            month (int): Month

        Returns:
            list: List of price history for the month
        """
        from calendar import monthrange

        start_date = datetime(year, month, 1).date()
        end_date = datetime(year, month, monthrange(year, month)[1]).date()

        return cls.get_price_range(stock_id, start_date, end_date)

    @classmethod
    def calculate_returns(cls, stock_id, days=30):
        """
        Calculate price returns over a period

        Args:
            stock_id (int): Stock ID
            days (int): Period in days

        Returns:
            dict: Return statistics
        """
        recent_prices = cls.get_recent_prices(stock_id, days)

        if len(recent_prices) < 2:
            return None

        start_price = recent_prices[0].close_price
        end_price = recent_prices[-1].close_price

        total_return = ((end_price - start_price) / start_price) * 100

        # Calculate daily returns
        daily_returns = []
        for i in range(1, len(recent_prices)):
            prev_price = recent_prices[i - 1].close_price
            curr_price = recent_prices[i].close_price
            daily_return = ((curr_price - prev_price) / prev_price) * 100
            daily_returns.append(daily_return)

        return {
            "total_return": round(total_return, 2),
            "daily_returns": daily_returns,
            "avg_daily_return": (
                round(sum(daily_returns) / len(daily_returns), 4)
                if daily_returns
                else 0
            ),
            "volatility": (
                round(cls._calculate_volatility(daily_returns), 4)
                if daily_returns
                else 0
            ),
        }

    @staticmethod
    def _calculate_volatility(returns):
        """
        Calculate volatility (standard deviation) of returns

        Args:
            returns (list): List of daily returns

        Returns:
            float: Volatility
        """
        if len(returns) < 2:
            return 0

        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        return variance**0.5

    def get_daily_change(self):
        """
        Calculate daily price change

        Returns:
            dict: Daily change information
        """
        change = self.close_price - self.open_price
        change_percent = (change / self.open_price) * 100 if self.open_price > 0 else 0

        return {
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "is_positive": change >= 0,
        }

    def get_price_range(self):
        """
        Get the trading range for the day

        Returns:
            dict: Price range information
        """
        range_amount = self.high_price - self.low_price
        range_percent = (
            (range_amount / self.open_price) * 100 if self.open_price > 0 else 0
        )

        return {
            "range": round(range_amount, 2),
            "range_percent": round(range_percent, 2),
            "high": self.high_price,
            "low": self.low_price,
        }

    def to_chart_data(self):
        """
        Convert to format suitable for charting

        Returns:
            dict: Chart data format
        """
        return {
            "date": self.date.isoformat(),
            "open": self.open_price,
            "high": self.high_price,
            "low": self.low_price,
            "close": self.close_price,
            "volume": self.volume or 0,
        }

    def to_dict(self):
        """
        Convert to dictionary format (for API)

        Returns:
            dict: Dictionary of price history information
        """
        base_dict = super().to_dict()
        base_dict.update(
            {
                "daily_change": self.get_daily_change(),
                "price_range": self.get_price_range(),
                "chart_data": self.to_chart_data(),
            }
        )
        return base_dict

    def __repr__(self):
        return f"<PriceHistory {self.stock.symbol if self.stock else self.stock_id} {self.date}: ${self.close_price}>"

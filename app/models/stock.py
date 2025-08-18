from app.models import db, BaseModel
from sqlalchemy import Index


class Stock(BaseModel):
    """
    Stock basic information model
    Manages basic stock information (ticker symbol, company name, etc.)
    """

    __tablename__ = "stocks"

    # basic information
    symbol = db.Column(db.String(20), unique=True, nullable=False, index=True)
    company_name = db.Column(db.String(200), nullable=False)
    exchange = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(10), default="US", nullable=False)
    currency = db.Column(db.String(10), default="USD", nullable=False)

    # sector information
    sector = db.Column(db.String(100), nullable=True)
    industry = db.Column(db.String(100), nullable=True)

    # market information
    market_cap = db.Column(db.BigInteger, nullable=True)
    shares_outstanding = db.Column(db.BigInteger, nullable=True)

    # current price information
    current_price = db.Column(db.Float, nullable=True)
    previous_close = db.Column(db.Float, nullable=True)
    day_change = db.Column(db.Float, nullable=True)
    day_change_percent = db.Column(db.Float, nullable=True)

    # meta information
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_updated = db.Column(db.DateTime, nullable=True)

    # relations
    price_history = db.relationship(
        "PriceHistory", backref="stock", lazy=True, cascade="all, delete-orphan"
    )
    watchlist_items = db.relationship(
        "Watchlist", backref="stock", lazy=True, cascade="all, delete-orphan"
    )

    # index settings
    __table_args__ = (
        Index("idx_symbol_country", "symbol", "country"),
        Index("idx_sector_country", "sector", "country"),
        Index("idx_active_symbol", "is_active", "symbol"),
    )

    def __init__(self, symbol, company_name, **kwargs):
        """
        Constructor

        Args:
        symbol (str): Ticker symbol
        company_name (str): Company name
        **kwargs: Other parameters
        """
        super().__init__()
        self.symbol = symbol.upper()  # Standardize to uppercase
        self.company_name = company_name

        # Set optional arguments
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @classmethod
    def find_by_symbol(cls, symbol, country="US"):
        """
        Search stock by ticker symbol

        Args:
        symbol (str): Ticker symbol
        country (str): Country code

        Returns:
        Stock: Found stock, None if not found
        """
        return cls.query.filter_by(
            symbol=symbol.upper(), country=country, is_active=True
        ).first()

    @classmethod
    def search_by_name(cls, query, limit=10):
        """
        Partial match search by company name

        Args:
        query (str): Search keyword
        limit (int): Maximum number of results

        Returns:
        list: List of search results
        """
        return (
            cls.query.filter(cls.company_name.ilike(f"%{query}%"), cls.is_active == True)
            .limit(limit)
            .all()
        )

    @classmethod
    def get_by_sector(cls, sector, limit=50):
        """
        Get stocks by sector

        Args:
        sector (str): Sector name
        limit (int): Maximum number of results

        Returns:
        list: List of stocks in the sector
        """
        return cls.query.filter_by(sector=sector, is_active=True).limit(limit).all()

    @classmethod
    def get_active_stocks(cls, limit=100):
        """
        Get active stocks list

        Args:
        limit (int): Maximum number of results

        Returns:
        list: List of active stocks
        """
        return cls.query.filter_by(is_active=True).limit(limit).all()

    def update_price_info(self, current_price, previous_close=None):
        """
        Update price information

        Args:
        current_price (float): Current price
        previous_close (float): Previous closing price
        """
        from datetime import datetime
        
        self.current_price = current_price

        if previous_close:
            self.previous_close = previous_close
            self.day_change = current_price - previous_close
            if previous_close > 0:
                self.day_change_percent = (self.day_change / previous_close) * 100

        self.last_updated = datetime.now(datetime.timezone.utc)

    def get_price_change_color(self):
        """
        Get color based on price change (for UI)

        Returns:
        str: CSS class name
        """
        if self.day_change is None:
            return "text-muted"
        elif self.day_change > 0:
            return "text-success"
        elif self.day_change < 0:
            return "text-danger"
        else:
            return "text-muted"

    def format_market_cap(self):
        """
        Format market cap in readable format

        Returns:
        str: Formatted market capitalization
        """
        if not self.market_cap:
            return "N/A"

        if self.market_cap >= 1_000_000_000_000:  # 1 trillion or more
            return f"${self.market_cap / 1_000_000_000_000:.2f}T"
        elif self.market_cap >= 1_000_000_000:  # 1 billion or more
            return f"${self.market_cap / 1_000_000_000:.2f}B"
        elif self.market_cap >= 1_000_000:  # 1 million or more
            return f"${self.market_cap / 1_000_000:.2f}M"
        else:
            return f"${self.market_cap:,.0f}"

    def to_dict(self):
        """
        Convert to dictionary format (for API)

        Returns:
        dict: Dictionary of stock information
        """
        base_dict = super().to_dict()
        base_dict.update(
            {
                "price_change_color": self.get_price_change_color(),
                "formatted_market_cap": self.format_market_cap(),
            }
        )
        return base_dict

    def __repr__(self):
        return f"<Stock {self.symbol}: {self.company_name}>"

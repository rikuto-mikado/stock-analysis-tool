from app.models import db, BaseModel
from sqlalchemy import Index, desc
from datetime import datetime


class Watchlist(BaseModel):
    """
    Watchlist model
    Manages user's favorite stocks for monitoring
    """

    __tablename__ = "watchlist"

    # Foreign key
    stock_id = db.Column(db.Integer, db.ForeignKey("stocks.id"), nullable=False)

    # User identification (for future multi-user support)
    user_id = db.Column(
        db.String(50), default="default", nullable=False
    )  # Session-based for now

    # Watchlist settings
    notes = db.Column(db.Text, nullable=True)  # User notes about the stock
    target_price = db.Column(db.Float, nullable=True)  # Target price for alerts
    stop_loss = db.Column(db.Float, nullable=True)  # Stop loss price

    # Alert settings
    price_alert_enabled = db.Column(db.Boolean, default=False, nullable=False)
    percent_change_threshold = db.Column(
        db.Float, default=5.0, nullable=True
    )  # Alert when change > 5%

    # Display settings
    display_order = db.Column(
        db.Integer, default=0, nullable=False
    )  # Order in watchlist
    is_favorite = db.Column(
        db.Boolean, default=False, nullable=False
    )  # Star/favorite flag

    # Metadata
    added_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_viewed = db.Column(db.DateTime, nullable=True)

    # Index settings
    __table_args__ = (
        Index("idx_user_stock", "user_id", "stock_id"),
        Index("idx_user_order", "user_id", "display_order"),
        Index("idx_user_favorite", "user_id", "is_favorite"),
        # Prevent duplicate entries
        db.UniqueConstraint("user_id", "stock_id", name="unique_user_stock"),
    )

    def __init__(self, stock_id, user_id="default", **kwargs):
        """
        Constructor

        Args:
            stock_id (int): Stock ID
            user_id (str): User identifier
            **kwargs: Other parameters
        """
        super().__init__()
        self.stock_id = stock_id
        self.user_id = user_id

        # Set display order to end of list if not specified
        if "display_order" not in kwargs:
            last_item = (
                Watchlist.query.filter_by(user_id=user_id)
                .order_by(desc(Watchlist.display_order))
                .first()
            )
            self.display_order = (last_item.display_order + 1) if last_item else 0

        # Set optional arguments
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @classmethod
    def get_user_watchlist(cls, user_id="default", include_favorites_first=True):
        """
        Get user's watchlist

        Args:
            user_id (str): User identifier
            include_favorites_first (bool): Show favorites first

        Returns:
            list: List of watchlist items
        """
        query = cls.query.filter_by(user_id=user_id)

        if include_favorites_first:
            # Order by: favorites first, then by display_order
            query = query.order_by(desc(cls.is_favorite), cls.display_order)
        else:
            query = query.order_by(cls.display_order)

        return query.all()

    @classmethod
    def add_to_watchlist(cls, stock_id, user_id="default", **kwargs):
        """
        Add stock to watchlist

        Args:
            stock_id (int): Stock ID
            user_id (str): User identifier
            **kwargs: Additional settings

        Returns:
            Watchlist: Created watchlist item, None if already exists
        """
        # Check if already exists
        existing = cls.query.filter_by(user_id=user_id, stock_id=stock_id).first()
        if existing:
            return None

        # Create new watchlist item
        watchlist_item = cls(stock_id=stock_id, user_id=user_id, **kwargs)
        if watchlist_item.save():
            return watchlist_item
        return None

    @classmethod
    def remove_from_watchlist(cls, stock_id, user_id="default"):
        """
        Remove stock from watchlist

        Args:
            stock_id (int): Stock ID
            user_id (str): User identifier

        Returns:
            bool: True if removed, False if not found
        """
        item = cls.query.filter_by(user_id=user_id, stock_id=stock_id).first()
        if item:
            return item.delete()
        return False

    @classmethod
    def is_in_watchlist(cls, stock_id, user_id="default"):
        """
        Check if stock is in watchlist

        Args:
            stock_id (int): Stock ID
            user_id (str): User identifier

        Returns:
            bool: True if in watchlist
        """
        return (
            cls.query.filter_by(user_id=user_id, stock_id=stock_id).first() is not None
        )

    @classmethod
    def get_favorites(cls, user_id="default"):
        """
        Get favorite stocks

        Args:
            user_id (str): User identifier

        Returns:
            list: List of favorite watchlist items
        """
        return (
            cls.query.filter_by(user_id=user_id, is_favorite=True)
            .order_by(cls.display_order)
            .all()
        )

    @classmethod
    def get_alert_enabled(cls, user_id="default"):
        """
        Get stocks with alerts enabled

        Args:
            user_id (str): User identifier

        Returns:
            list: List of watchlist items with alerts
        """
        return cls.query.filter_by(user_id=user_id, price_alert_enabled=True).all()

    @classmethod
    def reorder_watchlist(cls, user_id, stock_ids_in_order):
        """
        Reorder watchlist items

        Args:
            user_id (str): User identifier
            stock_ids_in_order (list): List of stock IDs in desired order

        Returns:
            bool: True if successful
        """
        try:
            for index, stock_id in enumerate(stock_ids_in_order):
                item = cls.query.filter_by(user_id=user_id, stock_id=stock_id).first()
                if item:
                    item.display_order = index
                    db.session.add(item)

            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error reordering watchlist: {e}")
            return False

    def toggle_favorite(self):
        """
        Toggle favorite status

        Returns:
            bool: New favorite status
        """
        self.is_favorite = not self.is_favorite
        self.save()
        return self.is_favorite

    def update_notes(self, notes):
        """
        Update user notes

        Args:
            notes (str): New notes

        Returns:
            bool: True if successful
        """
        self.notes = notes
        return self.save()

    def set_price_alert(
        self, target_price=None, stop_loss=None, enabled=True, threshold=5.0
    ):
        """
        Set price alert settings

        Args:
            target_price (float): Target price for alert
            stop_loss (float): Stop loss price
            enabled (bool): Enable/disable alerts
            threshold (float): Percentage change threshold

        Returns:
            bool: True if successful
        """
        if target_price is not None:
            self.target_price = target_price
        if stop_loss is not None:
            self.stop_loss = stop_loss

        self.price_alert_enabled = enabled
        self.percent_change_threshold = threshold

        return self.save()

    def update_last_viewed(self):
        """
        Update last viewed timestamp
        """
        self.last_viewed = datetime.utcnow()
        self.save()

    def should_alert(self, current_price):
        """
        Check if current price should trigger an alert

        Args:
            current_price (float): Current stock price

        Returns:
            dict: Alert information
        """
        if not self.price_alert_enabled:
            return {"should_alert": False}

        alerts = []

        # Check target price
        if self.target_price and current_price >= self.target_price:
            alerts.append(
                {
                    "type": "target_reached",
                    "message": f"Target price ${self.target_price} reached! Current: ${current_price}",
                }
            )

        # Check stop loss
        if self.stop_loss and current_price <= self.stop_loss:
            alerts.append(
                {
                    "type": "stop_loss",
                    "message": f"Stop loss ${self.stop_loss} triggered! Current: ${current_price}",
                }
            )

        # Check percentage change (requires previous price)
        if self.stock and self.stock.previous_close and self.percent_change_threshold:
            change_percent = abs(
                (
                    (current_price - self.stock.previous_close)
                    / self.stock.previous_close
                )
                * 100
            )
            if change_percent >= self.percent_change_threshold:
                direction = (
                    "up" if current_price > self.stock.previous_close else "down"
                )
                alerts.append(
                    {
                        "type": "percent_change",
                        "message": f"Price moved {direction} {change_percent:.1f}%! Current: ${current_price}",
                    }
                )

        return {"should_alert": len(alerts) > 0, "alerts": alerts}

    def get_performance_since_added(self):
        """
        Calculate performance since added to watchlist

        Returns:
            dict: Performance statistics
        """
        if not self.stock or not self.stock.current_price:
            return None

        # Get price history from when added
        from app.models.price_history import PriceHistory

        price_when_added = (
            PriceHistory.query.filter(
                PriceHistory.stock_id == self.stock_id,
                PriceHistory.date >= self.added_at.date(),
            )
            .order_by(PriceHistory.date.asc())
            .first()
        )

        if not price_when_added:
            return None

        start_price = price_when_added.close_price
        current_price = self.stock.current_price

        total_return = ((current_price - start_price) / start_price) * 100
        days_held = (datetime.utcnow() - self.added_at).days

        return {
            "start_price": start_price,
            "current_price": current_price,
            "total_return": round(total_return, 2),
            "days_held": days_held,
            "annualized_return": (
                round((total_return / max(days_held, 1)) * 365, 2)
                if days_held > 0
                else 0
            ),
        }

    def to_dict(self):
        """
        Convert to dictionary format (for API)

        Returns:
            dict: Dictionary of watchlist information
        """
        base_dict = super().to_dict()
        base_dict.update(
            {
                "stock_info": self.stock.to_dict() if self.stock else None,
                "performance": self.get_performance_since_added(),
                "days_in_watchlist": (datetime.utcnow() - self.added_at).days,
            }
        )
        return base_dict

    def __repr__(self):
        return f"<Watchlist {self.user_id}: {self.stock.symbol if self.stock else self.stock_id}>"

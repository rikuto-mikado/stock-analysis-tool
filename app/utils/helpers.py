import re
from datetime import datetime, timedelta
from typing import Optional, Union


def format_currency(amount: Optional[float], currency: str = "USD") -> str:
    """
    Format currency amount

    Args:
    amount: Amount to format
    currency: Currency code

    Returns:
    str: Formatted currency string
    """
    if amount is None:
        return "N/A"

    symbol = "$" if currency == "USD" else currency

    if amount >= 1_000_000_000:
        return f"{symbol}{amount / 1_000_000_000:.2f}B"
    elif amount >= 1_000_000:
        return f"{symbol}{amount / 1_000_000:.2f}M"
    elif amount >= 1_000:
        return f"{symbol}{amount / 1_000:.2f}K"
    else:
        return f"{symbol}{amount:.2f}"


def format_percentage(value: Optional[float], decimal_places: int = 2) -> str:
    """
    Format percentage value

    Args:
    value: Percentage value
    decimal_places: Number of decimal places

    Returns:
    str: Formatted percentage string
    """
    if value is None:
        return "N/A"

    return f"{value:.{decimal_places}f}%"


def format_large_number(number: Optional[Union[int, float]]) -> str:
    """
    Format large numbers with K, M, B suffixes

    Args:
    number: Number to format

    Returns:
    str: Formatted number string
    """
    if number is None:
        return "N/A"

    if number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.2f}B"
    elif number >= 1_000_000:
        return f"{number / 1_000_000:.2f}M"
    elif number >= 1_000:
        return f"{number / 1_000:.2f}K"
    else:
        return f"{number:,.0f}"


def calculate_change_percentage(current: float, previous: float) -> Optional[float]:
    """
    Calculate percentage change between two values

    Args:
    current: Current value
    previous: Previous value

    Returns:
    float: Percentage change or None if invalid
    """
    if previous == 0 or previous is None or current is None:
        return None

    return ((current - previous) / previous) * 100


def get_change_color_class(change: Optional[float]) -> str:
    """
    Get CSS class based on change value

    Args:
    change: Change value

    Returns:
    str: CSS class name
    """
    if change is None:
        return "text-muted"
    elif change > 0:
        return "text-success"
    elif change < 0:
        return "text-danger"
    else:
        return "text-muted"


def get_trading_days_ago(days: int) -> datetime:
    """
    Get datetime for trading days ago (excluding weekends)

    Args:
    days: Number of trading days

    Returns:
    datetime: Date for trading days ago
    """
    current_date = datetime.now()
    trading_days_count = 0

    while trading_days_count < days:
        current_date -= timedelta(days=1)
        # Skip weekends (Saturday=5, Sunday=6)
        if current_date.weekday() < 5:
            trading_days_count += 1

    return current_date


def safe_divide(
    numerator: Optional[float], denominator: Optional[float]
) -> Optional[float]:
    """
    Safely divide two numbers, handling None and zero cases

    Args:
    numerator: Numerator value
    denominator: Denominator value

    Returns:
    float: Division result or None if invalid
    """
    if numerator is None or denominator is None or denominator == 0:
        return None

    return numerator / denominator


def truncate_text(text: str, max_length: int = 50) -> str:
    """
    Truncate text to specified length

    Args:
    text: Text to truncate
    max_length: Maximum length

    Returns:
    str: Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - 3] + "..."


def is_market_open() -> bool:
    """
    Check if US stock market is currently open
    Simple implementation - can be enhanced with holiday checking

    Returns:
        bool: True if market is open
    """
    now = datetime.now()

    if now.weekday() >= 5:  # Saturday or Sunday
        return False

    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)

    return market_open <= now <= market_close

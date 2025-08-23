import re
from typing import Optional, List, Tuple


def validate_stock_symbol(symbol: str) -> Tuple[bool, Optional[str]]:
    """
    Validate stock ticker symbol

    Args:
    symbol: Ticker symbol to validate

    Returns:
    tuple: (is_valid, error_message)
    """
    if not symbol:
        return False, "Symbol cannot be empty"

    symbol = symbol.strip().upper()

    # Check length (most symbols are 1-5 characters)
    if len(symbol) < 1 or len(symbol) > 6:
        return False, "Symbol must be 1-6 characters long"

    # Check for valid characters (letters and numbers only)
    if not re.match(r"^[A-Z0-9]+$", symbol):
        return False, "Symbol can only contain letters and numbers"

    # Check if it starts with a letter
    if not symbol[0].isalpha():
        return False, "Symbol must start with a letter"

    return True, None


def validate_price(price: str) -> Tuple[bool, Optional[float], Optional[str]]:
    """
    Validate and convert price string to float

    Args:
    price: Price string to validate

    Returns:
    tuple: (is_valid, converted_price, error_message)
    """
    if not price:
        return False, None, "Price cannot be empty"

    # Remove whitespace and dollar signs
    price = price.strip().replace("$", "").replace(",", "")

    try:
        price_float = float(price)

        # Check for reasonable range
        if price_float < 0:
            return False, None, "Price cannot be negative"

        if price_float > 1_000_000:
            return False, None, "Price seems unreasonably high"

        return True, round(price_float, 2), None

    except ValueError:
        return False, None, "Invalid price format"


def validate_percentage(percentage: str) -> Tuple[bool, Optional[float], Optional[str]]:
    """
    Validate percentage string

    Args:
    percentage: Percentage string to validate

    Returns:
    tuple: (is_valid, converted_percentage, error_message)
    """
    if not percentage:
        return False, None, "Percentage cannot be empty"

    # Remove whitespace and percentage signs
    percentage = percentage.strip().replace("%", "")

    try:
        percentage_float = float(percentage)

        # Check for reasonable range (-100% to +1000%)
        if percentage_float < -100:
            return False, None, "Percentage cannot be less than -100%"

        if percentage_float > 1000:
            return False, None, "Percentage seems unreasonably high"

        return True, round(percentage_float, 2), None

    except ValueError:
        return False, None, "Invalid percentage format"


def validate_date_range(start_date: str, end_date: str) -> Tuple[bool, Optional[str]]:
    """
    Validate date range

    Args:
    start_date: Start date string (YYYY-MM-DD)
    end_date: End date string (YYYY-MM-DD)

    Returns:
    tuple: (is_valid, error_message)
    """

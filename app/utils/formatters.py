from typing import Optional


def format_market_cap(market_cap: Optional[float]) -> str:
    """
    Format market capitalization

    Args:
        market_cap: Market cap value

    Returns:
        str: Formatted market cap
    """
    if not market_cap:
        return "N/A"

    if market_cap >= 1_000_000_000_000:
        return f"${market_cap / 1_000_000_000_000:.2f}T"
    elif market_cap >= 1_000_000_000:
        return f"${market_cap / 1_000_000_000:.2f}B"
    elif market_cap >= 1_000_000:
        return f"${market_cap / 1_000_000:.2f}M"
    else:
        return f"${market_cap:,.0f}"


def format_volume(volume: Optional[int]) -> str:
    """
    Format trading volume

    Args:
        volume: Volume value

    Returns:
        str: Formatted volume
    """
    if not volume:
        return "N/A"

    if volume >= 1_000_000_000:
        return f"{volume / 1_000_000_000:.2f}B"
    elif volume >= 1_000_000:
        return f"{volume / 1_000_000:.2f}M"
    elif volume >= 1_000:
        return f"{volume / 1_000:.2f}K"
    else:
        return f"{volume:,}"

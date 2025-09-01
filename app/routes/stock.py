from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app.services.stock_api import StockAPIService
from app.utils.validators import validate_stock_symbol
from app.utils.helpers import format_currency, format_percentage, get_change_color_class
from app.models.stock import Stock
from app.models.watchlist import Watchlist

# Create Blueprint for stock routes
bp = Blueprint("stock", __name__, url_prefix="/stock")

# Initialize tock API service
stock_api = StockAPIService()


@bp.route("/<symbol>")
def detail(symbol):
    """
    Stock detail page

    Args:
    symbol (str): Stock symbol

    Returns:
    str: Rendered stock detail page
    """
    # Validate symbol
    is_valid, error_msg = validate_stock_symbol(symbol)
    if not is_valid:
        flash(f"Invalid stock symbol: {error_msg}", "error")
        return redirect(url_for("search.index"))

    symbol = symbol.upper()

    # Getstock infromation from API
    stock_info = stock_api.get_stock_info(symbol)

    if not stock_info:
        flash(f'Stock "{symbol}" not found', "error")
        return redirect(url_for("search.index"))

    # Check if stock is in watchlist
    in_watchlist = False
    stock_db = Stock.find_by_symbol(symbol)
    if stock_db:
        in_watchlist = Watchlist.is_in_watchlist(stock_db.id)

    # Calculate additional metrics
    current_price = stock_info.get("current_price", 0)
    previous_close = stock_info.get("previous_close", 0)

    if previous_close and current_price:
        day_change = current_price - previous_close
        day_change_percent = (day_change / previous_close) * 100
        change_color = get_change_color_class(day_change)

        stock_info.update(
            {
                "day_change": day_change,
                "day_change_percent": day_change_percent,
                "change_color": change_color,
                "formatted_day_change": format_currency(abs(day_change)),
                "formatted_day_change_percent": format_percentage(day_change_percent),
            }
        )

    stock_info.update(
        {
            "formatted_current_price": format_currency(current_price),
            "formatted_previous_close": format_currency(previous_close),
            "formatted_market_cap": format_currency(stock_info.get("market_cap")),
            "formatted_volume": (
                f"{stock_info.get('volume', 0):,}"
                if stock_info.get("volume")
                else "N/A"
            ),
        }
    )

    # Format additional fields for display
    stock_info.update(
        {
            "formatted_current_price": format_currency(current_price),
            "formatted_previous_close": format_currency(previous_close),
            "formatted_market_cap": format_currency(stock_info.get("market_cap")),
            "formatted_volume": (
                f"{stock_info.get('volume', 0):,}"
                if stock_info.get("volume")
                else "N/A"
            ),
        }
    )

    return render_template(
        "stock/detail.html",
        title=f"{symbol} - {stock_info.get('company_name', symbol)}",
        stock=stock_info,
        in_watchlist=in_watchlist,
    )

@bp.route('/api/<symbol>/refresh')

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app.services.stock_api import StockAPIService
from app.utils.validators import validate_search_query, validate_stock_symbol
from app.models.stock import Stock

# Create Blueprint for search routes
bp = Blueprint("search", __name__, url_prefix="/search")

# Initialize stock API service
stock_api = StockAPIService()


@bp.route("/")
def index():
    """
    Search page

    Returns:
    str: Rendered search page
    """
    return render_template("stock/search.html", title="Stock Search")


@bp.route("/api/suggestions")
def search_suggestions():
    """
    API endpoint for search suggestions

    Returns:
    json: List of matching stocks
    """
    query = request.args.get("q", "").stript()

    if not query:
        return jsonify({"results": []})

    # Validate search query
    is_valid, error_msg = validate_search_query(query)
    if not is_valid:
        return jsonify({"error": error_msg}), 400

    # Search using stock API service
    suggestions = stock_api.search_stocks(query)

    return jsonify({"results": suggestions})


@bp.route("/api/quote/<symbol>")
def get_quote(symbol):
    """
    API endpoint to get stock quote

    Args:
    symbol (str): Stock symbol

    Returns:
    json: Stock information
    """
    # Validate symbol
    is_valid, error_msg = validate_stock_symbol(symbol)
    if not is_valid:
        return jsonify({"error": error_msg}), 400

    # Get stock info from API
    stock_info = stock_api.get_stock_info(symbol)

    if not stock_info:
        return jsonify({"error": f"Stock {symbol} not found"}), 404

    return jsonify({"stock": stock_info})


@bp.route("/results")
def search_results():
    """
    Search results page

    Returns:
    str: Rendered search results or redirect
    """
    query = request.args.get("q", "").strip()

    if not query:
        flash("Please enter a search term", "warning")
        return redirect(url_for("search.index"))

    # Validate search query
    is_valid, error_msg = validate_search_query(query)
    if not is_valid:
        flash(f"Invalid search: {error_msg}", "error")
        return redirect(url_for("search.index"))

    # Check if it's a direct symbol lookup
    symbol_valid, _ = validate_stock_symbol(query)
    if symbol_valid:
        # Redirect to stock detail page
        return redirect(url_for("stock.detail", symbol=query.upper()))

    # Search for suggestions
    results = stock_api.search_stocks(query)

    return render_template(
        "stock/search.html",
        title=f'Search Results for "{query}"',
        query=query,
        results=results,
    )

from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    flash,
    session,
)
from app.services.stock_api import StockAPIService
from app.models.stock import Stock
from app.models.watchlist import Watchlist
from app.models import db
from app.utils.validators import validate_stock_symbol, validate_watchlist_note
from app.utils.helpers import format_currency, format_percentage, get_change_color_class

# Create Blueprint for watchlist routes
bp = Blueprint("watchlist", __name__, url_prefix="/watchlist")

# Initialize stock API service
stock_api = StockAPIService()


@bp.route("/")
def list():
    """
    Watchlist page - shows user's saved stocks

    Returns:
        str: Rendered watchlist page
    """
    try:
        # Get user ID from session (default for now)
        user_id = session.get("user_id", "default")

        # Get user's watchlist
        watchlist_items = Watchlist.get_user_watchlist(
            user_id, include_favorites_first=True
        )

        # Enhance watchlist items with current stock data
        enhanced_watchlist = []
        for item in watchlist_items:
            if item.stock:
                # Get fresh stock data if needed
                stock_data = item.stock.to_dict()

                # Add watchlist-specific data
                stock_data.update(
                    {
                        "watchlist_id": item.id,
                        "added_at": item.added_at,
                        "is_favorite": item.is_favorite,
                        "notes": item.notes,
                        "target_price": item.target_price,
                        "stop_loss": item.stop_loss,
                        "price_alert_enabled": item.price_alert_enabled,
                        "days_in_watchlist": item.to_dict().get("days_in_watchlist", 0),
                        "performance": item.get_performance_since_added(),
                    }
                )

                enhanced_watchlist.append(stock_data)

        return render_template(
            "watchlist/list.html",
            title="My Watchlist",
            watchlist=enhanced_watchlist,
            watchlist_count=len(enhanced_watchlist),
        )

    except Exception as e:
        flash(f"Error loading watchlist: {str(e)}", "error")
        return redirect(url_for("main.index"))


@bp.route("/manage")
def manage():
    """
    Watchlist management page

    Returns:
        str: Rendered management page
    """
    try:
        # Get user ID from session
        user_id = session.get("user_id", "default")

        # Get watchlist with additional details
        watchlist_items = Watchlist.get_user_watchlist(user_id)

        # Get favorites
        favorites = Watchlist.get_favorites(user_id)

        # Get alert-enabled items
        alerts = Watchlist.get_alert_enabled(user_id)

        return render_template(
            "watchlist/manage.html",
            title="Manage Watchlist",
            watchlist=watchlist_items,
            favorites=favorites,
            alerts=alerts,
        )

    except Exception as e:
        flash(f"Error loading watchlist management: {str(e)}", "error")
        return redirect(url_for("watchlist.list"))


# API Endpoints


@bp.route("/api/add", methods=["POST"])
def api_add():
    """
    API endpoint to add stock to watchlist

    Returns:
        json: Result of addition
    """
    try:
        data = request.get_json()
        symbol = data.get("symbol", "").strip().upper()
        user_id = session.get("user_id", "default")

        # Validate symbol
        is_valid, error_msg = validate_stock_symbol(symbol)
        if not is_valid:
            return jsonify({"error": error_msg}), 400

        # Check if stock exists in database, if not create it
        stock = Stock.find_by_symbol(symbol)
        if not stock:
            # Get stock info from API
            stock_info = stock_api.get_stock_info(symbol)
            if not stock_info:
                return jsonify({"error": f"Stock {symbol} not found"}), 404

            # Create new stock record
            stock = Stock(
                symbol=symbol,
                company_name=stock_info.get("company_name", symbol),
                exchange=stock_info.get("exchange"),
                sector=stock_info.get("sector"),
                industry=stock_info.get("industry"),
                country=stock_info.get("country", "US"),
                currency=stock_info.get("currency", "USD"),
                market_cap=stock_info.get("market_cap"),
                current_price=stock_info.get("current_price"),
                previous_close=stock_info.get("previous_close"),
            )

            if not stock.save():
                return jsonify({"error": "Failed to save stock data"}), 500

        # Check if already in watchlist
        if Watchlist.is_in_watchlist(stock.id, user_id):
            return jsonify({"error": f"{symbol} is already in your watchlist"}), 400

        # Add to watchlist
        watchlist_item = Watchlist.add_to_watchlist(
            stock_id=stock.id,
            user_id=user_id,
            notes=data.get("notes", ""),
            target_price=data.get("target_price"),
            stop_loss=data.get("stop_loss"),
            price_alert_enabled=data.get("price_alert_enabled", False),
        )

        if watchlist_item:
            return jsonify(
                {
                    "message": f"{symbol} added to watchlist successfully",
                    "watchlist_id": watchlist_item.id,
                    "stock": stock.to_dict(),
                }
            )
        else:
            return jsonify({"error": "Failed to add to watchlist"}), 500

    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500


@bp.route("/api/remove", methods=["POST"])
def api_remove():
    """
    API endpoint to remove stock from watchlist

    Returns:
        json: Result of removal
    """
    try:
        data = request.get_json()
        user_id = session.get("user_id", "default")

        # Handle removal by symbol or watchlist ID
        if "symbol" in data:
            symbol = data["symbol"].strip().upper()

            # Validate symbol
            is_valid, error_msg = validate_stock_symbol(symbol)
            if not is_valid:
                return jsonify({"error": error_msg}), 400

            # Find stock
            stock = Stock.find_by_symbol(symbol)
            if not stock:
                return jsonify({"error": f"Stock {symbol} not found"}), 404

            stock_id = stock.id

        elif "watchlist_id" in data:
            watchlist_id = data["watchlist_id"]

            # Find watchlist item
            watchlist_item = Watchlist.query.filter_by(
                id=watchlist_id, user_id=user_id
            ).first()

            if not watchlist_item:
                return jsonify({"error": "Watchlist item not found"}), 404

            stock_id = watchlist_item.stock_id
            symbol = watchlist_item.stock.symbol if watchlist_item.stock else "Unknown"

        else:
            return jsonify({"error": "Symbol or watchlist_id required"}), 400

        # Remove from watchlist
        if Watchlist.remove_from_watchlist(stock_id, user_id):
            return jsonify({"message": f"{symbol} removed from watchlist successfully"})
        else:
            return jsonify({"error": "Failed to remove from watchlist"}), 500

    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500


@bp.route("/api/list")
def api_list():
    """
    API endpoint to get user's watchlist

    Returns:
        json: Watchlist data
    """
    try:
        user_id = session.get("user_id", "default")
        watchlist_items = Watchlist.get_user_watchlist(user_id)

        watchlist_data = []
        for item in watchlist_items:
            item_data = item.to_dict()
            watchlist_data.append(item_data)

        return jsonify({"watchlist": watchlist_data, "count": len(watchlist_data)})

    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500


@bp.route("/api/update", methods=["POST"])
def api_update():
    """
    API endpoint to update watchlist item settings

    Returns:
        json: Update result
    """
    try:
        data = request.get_json()
        user_id = session.get("user_id", "default")
        watchlist_id = data.get("watchlist_id")

        if not watchlist_id:
            return jsonify({"error": "Watchlist ID required"}), 400

        # Find watchlist item
        watchlist_item = Watchlist.query.filter_by(
            id=watchlist_id, user_id=user_id
        ).first()

        if not watchlist_item:
            return jsonify({"error": "Watchlist item not found"}), 404

        # Update fields if provided
        updated_fields = []

        if "notes" in data:
            is_valid, error_msg = validate_watchlist_note(data["notes"])
            if not is_valid:
                return jsonify({"error": f"Invalid notes: {error_msg}"}), 400

            watchlist_item.notes = data["notes"]
            updated_fields.append("notes")

        if "target_price" in data:
            watchlist_item.target_price = data["target_price"]
            updated_fields.append("target_price")

        if "stop_loss" in data:
            watchlist_item.stop_loss = data["stop_loss"]
            updated_fields.append("stop_loss")

        if "price_alert_enabled" in data:
            watchlist_item.price_alert_enabled = data["price_alert_enabled"]
            updated_fields.append("price_alert_enabled")

        if "percent_change_threshold" in data:
            watchlist_item.percent_change_threshold = data["percent_change_threshold"]
            updated_fields.append("percent_change_threshold")

        if "is_favorite" in data:
            watchlist_item.is_favorite = data["is_favorite"]
            updated_fields.append("is_favorite")

        # Save changes
        if watchlist_item.save():
            return jsonify(
                {
                    "message": "Watchlist item updated successfully",
                    "updated_fields": updated_fields,
                    "watchlist_item": watchlist_item.to_dict(),
                }
            )
        else:
            return jsonify({"error": "Failed to update watchlist item"}), 500

    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500


@bp.route("/api/toggle-favorite", methods=["POST"])
def api_toggle_favorite():
    """
    API endpoint to toggle favorite status

    Returns:
        json: Toggle result
    """
    try:
        data = request.get_json()
        user_id = session.get("user_id", "default")
        watchlist_id = data.get("watchlist_id")

        if not watchlist_id:
            return jsonify({"error": "Watchlist ID required"}), 400

        # Find watchlist item
        watchlist_item = Watchlist.query.filter_by(
            id=watchlist_id, user_id=user_id
        ).first()

        if not watchlist_item:
            return jsonify({"error": "Watchlist item not found"}), 404

        # Toggle favorite status
        new_status = watchlist_item.toggle_favorite()

        return jsonify(
            {
                "message": "Favorite status updated",
                "is_favorite": new_status,
                "symbol": (
                    watchlist_item.stock.symbol if watchlist_item.stock else "Unknown"
                ),
            }
        )

    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500


@bp.route("/api/reorder", methods=["POST"])
def api_reorder():
    """
    API endpoint to reorder watchlist items

    Returns:
        json: Reorder result
    """
    try:
        data = request.get_json()
        user_id = session.get("user_id", "default")
        stock_ids_in_order = data.get("stock_ids", [])

        if not stock_ids_in_order:
            return jsonify({"error": "Stock IDs array required"}), 400

        # Reorder watchlist
        if Watchlist.reorder_watchlist(user_id, stock_ids_in_order):
            return jsonify({"message": "Watchlist reordered successfully"})
        else:
            return jsonify({"error": "Failed to reorder watchlist"}), 500

    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500


@bp.route("/api/check/<symbol>")
def api_check(symbol):
    """
    API endpoint to check if stock is in watchlist

    Args:
        symbol (str): Stock symbol

    Returns:
        json: Check result
    """
    try:
        # Validate symbol
        is_valid, error_msg = validate_stock_symbol(symbol)
        if not is_valid:
            return jsonify({"error": error_msg}), 400

        symbol = symbol.upper()
        user_id = session.get("user_id", "default")

        # Find stock
        stock = Stock.find_by_symbol(symbol)
        if not stock:
            return jsonify({"in_watchlist": False, "symbol": symbol})

        # Check if in watchlist
        in_watchlist = Watchlist.is_in_watchlist(stock.id, user_id)

        return jsonify(
            {"in_watchlist": in_watchlist, "symbol": symbol, "stock_id": stock.id}
        )

    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500

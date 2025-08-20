#!/usr/bin/env python3
"""
Database initialization script
Creates database tables and populates with sample data
"""

import os
import sys
from datetime import datetime, date, timedelta

# Add the parent directory to Python path to import our app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db, init_db
from app.models.stock import Stock
from app.models.price_history import PriceHistory
from app.models.watchlist import Watchlist


def create_database():
    """Create database tables"""
    print("Creating database tables...")

    # Create Flask app
    app = create_app("development")

    with app.app_context():
        # Drop all tables first (for clean setup)
        db.drop_all()
        print("Dropped existing tables")

        # Create all tables
        db.create_all()
        print("Created all tables successfully")

        return app


def populate_sample_data():
    """Populate database with sample data"""
    print("Populating sample data...")

    # Sample stocks data
    sample_stocks = [
        {
            "symbol": "AAPL",
            "company_name": "Apple Inc.",
            "exchange": "NASDAQ",
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "country": "US",
            "currency": "USD",
            "market_cap": 3000000000000,  # $3T
            "current_price": 150.25,
            "previous_close": 148.30,
        },
        {
            "symbol": "GOOGL",
            "company_name": "Alphabet Inc.",
            "exchange": "NASDAQ",
            "sector": "Technology",
            "industry": "Internet Content & Information",
            "country": "US",
            "currency": "USD",
            "market_cap": 2000000000000,  # $2T
            "current_price": 2850.75,
            "previous_close": 2820.50,
        },
        {
            "symbol": "MSFT",
            "company_name": "Microsoft Corporation",
            "exchange": "NASDAQ",
            "sector": "Technology",
            "industry": "Software",
            "country": "US",
            "currency": "USD",
            "market_cap": 2800000000000,  # $2.8T
            "current_price": 380.90,
            "previous_close": 375.20,
        },
        {
            "symbol": "TSLA",
            "company_name": "Tesla, Inc.",
            "exchange": "NASDAQ",
            "sector": "Consumer Cyclical",
            "industry": "Auto Manufacturers",
            "country": "US",
            "currency": "USD",
            "market_cap": 800000000000,  # $800B
            "current_price": 248.50,
            "previous_close": 252.75,
        },
        {
            "symbol": "NVDA",
            "company_name": "NVIDIA Corporation",
            "exchange": "NASDAQ",
            "sector": "Technology",
            "industry": "Semiconductors",
            "country": "US",
            "currency": "USD",
            "market_cap": 1500000000000,  # $1.5T
            "current_price": 875.25,
            "previous_close": 862.10,
        },
    ]

    # Create stock records
    created_stocks = []
    for stock_data in sample_stocks:
        stock = Stock(
            symbol=stock_data["symbol"],
            company_name=stock_data["company_name"],
            **{
                k: v
                for k, v in stock_data.items()
                if k not in ["symbol", "company_name"]
            },
        )

        # Calculate day change
        if stock_data.get("current_price") and stock_data.get("previous_close"):
            stock.update_price_info(
                stock_data["current_price"], stock_data["previous_close"]
            )

        if stock.save():
            created_stocks.append(stock)
            print(f"Created stock: {stock.symbol} - {stock.company_name}")
        else:
            print(f"Failed to create stock: {stock_data['symbol']}")

    return created_stocks


def create_sample_price_history(stocks):
    """Create sample price history data"""
    print("Creating sample price history...")

    for stock in stocks:
        print(f"Creating price history for {stock.symbol}...")

        # Create 30 days of sample data
        base_date = date.today() - timedelta(days=30)
        base_price = stock.current_price or 100.0

        for i in range(30):
            current_date = base_date + timedelta(days=i)

            # Skip weekends (simplified)
            if current_date.weekday() >= 5:
                continue

            # Generate realistic price data with some volatility
            import random

            # Add some random walk behavior
            price_change = random.uniform(-0.05, 0.05)  # ±5% daily change
            day_price = base_price * (1 + price_change)

            # Generate OHLC data
            open_price = day_price * random.uniform(0.98, 1.02)
            close_price = day_price * random.uniform(0.98, 1.02)
            high_price = max(open_price, close_price) * random.uniform(1.00, 1.03)
            low_price = min(open_price, close_price) * random.uniform(0.97, 1.00)

            # Generate volume
            volume = random.randint(1000000, 10000000)

            # Create price history record
            price_history = PriceHistory(
                stock_id=stock.id,
                date=current_date,
                timestamp=datetime.combine(current_date, datetime.min.time()),
                open_price=round(open_price, 2),
                high_price=round(high_price, 2),
                low_price=round(low_price, 2),
                close_price=round(close_price, 2),
                volume=volume,
            )

            if not price_history.save():
                print(
                    f"Failed to create price history for {stock.symbol} on {current_date}"
                )

        print(f"Created 30 days of price history for {stock.symbol}")


def create_sample_watchlist(stocks):
    """Create sample watchlist entries"""
    print("Creating sample watchlist...")

    # Add first 3 stocks to watchlist
    for i, stock in enumerate(stocks[:3]):
        watchlist_item = Watchlist(
            stock_id=stock.id,
            user_id="default",
            notes=f"Sample watchlist item for {stock.company_name}",
            target_price=(
                stock.current_price * 1.1 if stock.current_price else None
            ),  # 10% above current
            is_favorite=(i == 0),  # Make first one favorite
            price_alert_enabled=True,
            percent_change_threshold=5.0,
        )

        if watchlist_item.save():
            print(f"Added {stock.symbol} to watchlist")
        else:
            print(f"Failed to add {stock.symbol} to watchlist")


def verify_database():
    """Verify database was created correctly"""
    print("\nVerifying database...")

    try:
        # Count records
        stock_count = Stock.query.count()
        price_count = PriceHistory.query.count()
        watchlist_count = Watchlist.query.count()

        print(f"Stocks: {stock_count}")
        print(f"Price History Records: {price_count}")
        print(f"Watchlist Items: {watchlist_count}")

        # Test some queries
        print("\nTesting queries...")

        # Test stock search
        apple = Stock.find_by_symbol("AAPL")
        if apple:
            print(f"Found Apple: {apple.company_name} - ${apple.current_price}")

        # Test price history
        if apple:
            latest_price = PriceHistory.get_latest_price(apple.id)
            if latest_price:
                print(
                    f"Latest price for Apple: ${latest_price.close_price} on {latest_price.date}"
                )

        # Test watchlist
        watchlist = Watchlist.get_user_watchlist()
        print(f"Watchlist items: {len(watchlist)}")

        print("\nDatabase verification completed successfully!")
        return True

    except Exception as e:
        print(f"Database verification failed: {e}")
        return False


def main():
    """Main initialization function"""
    print("Stock Analysis Tool - Database Initialization")
    print("=" * 50)

    try:
        # Create database
        app = create_database()

        with app.app_context():
            # Populate sample data
            stocks = populate_sample_data()

            if stocks:
                # Create price history
                create_sample_price_history(stocks)

                # Create watchlist
                create_sample_watchlist(stocks)

                # Verify everything
                if verify_database():
                    print("\n" + "=" * 50)
                    print("Database initialization completed successfully!")
                    print("You can now run the Flask application with: python app.py")
                else:
                    print("Database verification failed!")
                    return False
            else:
                print("Failed to create sample stocks!")
                return False

    except Exception as e:
        print(f"Error during database initialization: {e}")
        return False

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

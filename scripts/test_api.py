"""
Test script for Stock API integration
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.stock_api import StockAPIService


def test_stock_api():
    """Test the stock API service"""
    print("Testing Stock API Service...")

    api = StockAPIService()

    # Test stock info retrieval
    print("\n1. Testing stock info retrieval:")
    stock_info = api.get_stock_info("AAPL")
    if stock_info:
        print(f"AAPL: {stock_info['company_name']} - ${stock_info['current_price']}")
    else:
        print("Failed to get AAPL info")

    # Test symbol validation
    print("\n2. Testing symbol validation:")
    valid = api.validate_symbol("AAPL")
    print(f"AAPL validation: {valid}")

    # Test search
    print("\n3. Testing stock search:")
    results = api.search_stocks("Apple")
    print(f"Search results for 'Apple': {len(results)} found")
    for result in results[:3]:
        print(f"   - {result['symbol']}: {result['name']}")


if __name__ == "__main__":
    test_stock_api()

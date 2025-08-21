# Stock Analysis Tool

A comprehensive web-based stock analysis application built with Flask that provides real-time stock data, portfolio tracking, and market insights.

## Features

- **Real-time Stock Data**: Get live stock prices and market data.
- **Interactive Dashboard**: Visual charts and analytics for stock performance.
- **Watchlist Management**: Create and manage custom stock watchlists.
- **Stock Search**: Search and discover stocks with advanced filtering.
- **Price Alerts**: Set up automated alerts for price movements.
- **Stock Comparison**: Compare multiple stocks side-by-side.
- **Portfolio Tracking**: Monitor your investment portfolio performance.
- **Responsive Design**: Mobile-friendly interface.

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLAlchemy with SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Stock Data**: 
  - **Yahoo Finance (yfinance)**: For real-time and historical price data.
  - **Finnhub**: For company profiles, market news, and real-time quotes.
  - **Alpha Vantage**: For stock symbol search.
- **Charts**: Interactive JavaScript charting
- **Real-time Updates**: WebSocket integration

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd stock-analysis-tool
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your-secret-key-here
   FLASK_ENV=development
   DATABASE_URL=sqlite:///stock_analysis.db
   ALPHA_VANTAGE_API_KEY=your-api-key  # Required for stock search functionality
   FINNHUB_API_KEY=your-api-key        # Required for company profiles, news, and quotes
   TIMEZONE=Asia/Tokyo
   DEFAULT_CURRENCY=JPY
   ```

5. **Initialize the database**
   ```bash
   python scripts/init_db.py
   ```

6. **Seed sample data** (Optional)
   ```bash
   python scripts/seed_data.py
   ```

## Usage

1. **Start the development server**
   ```bash
   python app.py
   ```

2. **Access the application**
   Open your browser and navigate to `http://localhost:5001`

## Project Structure

```
stock-analysis-tool/
├── .gitignore
├── app.py
├── config.py
├── LICENSE
├── README.md
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── alert.py
│   │   ├── price_history.py
│   │   ├── stock.py
│   │   ├── user.py
│   │   └── watchlist.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── api.py
│   │   ├── main.py
│   │   ├── search.py
│   │   ├── stock.py
│   │   └── watchlist.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── alert_service.py
│   │   ├── cache_service.py
│   │   ├── data_processor.py
│   │   └── stock_api.py
│   ├── static/
│   │   ├── css/
│   │   │   ├── components.css
│   │   │   ├── dashboard.css
│   │   │   └── main.css
│   │   ├── img/
│   │   │   └── favicon.ico
│   │   └── js/
│   │       ├── charts.js
│   │       ├── main.js
│   │       ├── search.js
│   │       └── websocket.js
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── index.html
│   │   ├── components/
│   │   │   ├── chart.html
│   │   │   ├── navbar.html
│   │   │   └── stock_card.html
│   │   ├── errors/
│   │   │   ├── 404.html
│   │   │   └── 500.html
│   │   ├── stock/
│   │   │   ├── compare.html
│   │   │   ├── detail.html
│   │   │   └── search.html
│   │   └── watchlist/
│   │       ├── list.html
│   │       └── manage.html
│   └── utils/
│       ├── __init__.py
│       ├── formatters.py
│       ├── helpers.py
│       └── validators.py
├── docs/
│   ├── API.md
│   ├── DEPLOYMENT.md
│   ├── README.md
│   └── SETUP.md
├── instance/
├── migrations/
│   └── versions/
├── scheduler/
│   ├── scheduler.py
│   └── tasks.py
├── scripts/
│   ├── backup.py
│   ├── init_db.py
│   └── seed_data.py
└── tests/
    ├── conftest.py
    ├── test_models.py
    ├── test_routes.py
    └── test_services.py
```

## API Documentation

For detailed API documentation, see [docs/API.md](docs/API.md).

## Deployment

For deployment instructions, see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Development Setup

For detailed development setup instructions, see [docs/SETUP.md](docs/SETUP.md).

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

## Support

For questions or support, please open an issue on the repository.
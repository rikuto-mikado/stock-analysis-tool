import os
from app import create_app

# Get the setting from environment variable
config_name = os.environ.get("FLASK_ENV") or "development"

# Create the Flask application
app = create_app(config_name)

if __name__ == "__main__":
    # Run the server
    app.run(host="0.0.0.0", port=5000, debug=True)

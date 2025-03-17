import os
from app import app

if __name__ == "__main__":
    # Get port from environment variable or default to 5000
    port = int(os.environ.get("PORT", 5000))
    # Always bind to 0.0.0.0 for Replit deployment
    app.run(host='0.0.0.0', port=port, debug=True)
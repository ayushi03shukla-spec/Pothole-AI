"""
run.py
Entry point. `python run.py` starts the dev server.
For deployment (Render/Railway) use: gunicorn run:app
"""

import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

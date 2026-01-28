#!/bin/bash
# Run Edge Atlas Web Application locally

echo "Starting EDGE ATLAS V5.0 Web Application..."
echo "Access at: http://localhost:8080"
echo ""

# Set default port
export PORT=${PORT:-8080}

# Run with gunicorn (production-like) or python (development)
if command -v gunicorn &> /dev/null; then
    gunicorn edge_atlas_app:server --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0
else
    python edge_atlas_app.py
fi

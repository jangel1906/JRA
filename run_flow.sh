#!/bin/bash

# Flow - Intelligent Task Management Launcher

echo "✨ Starting Flow - Intelligent Task Management..."
echo "=================================================="
echo ""
echo "The application will be available at:"
echo "  Local:    http://localhost:8052"
echo "  Network:  http://$(hostname -I | awk '{print $1}'):8052"
echo ""
echo "Features:"
echo "  ✅ Smart task prioritization"
echo "  ✅ Energy-based scheduling"
echo "  ✅ Focus mode & Pomodoro timer"
echo "  ✅ Beautiful analytics"
echo "  ✅ Mobile PWA support"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""
echo "=================================================="
echo ""

# Run the application
python flow_app.py

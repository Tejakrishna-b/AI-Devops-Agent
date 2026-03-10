#!/bin/bash
# Launch AI DevOps Agent Web UI

echo "🚀 Starting AI DevOps Agent Web UI..."
echo ""
echo "The UI will open automatically in your browser"
echo "URL: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 -m streamlit run app.py

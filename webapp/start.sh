#!/bin/bash
# CHRONOS Web App Startup Script

echo "=================================="
echo "🚀 CHRONOS Web Application"
echo "=================================="
echo ""

# Check if Neo4j is running
echo "📊 Checking Neo4j status..."
if systemctl is-active --quiet neo4j || pgrep -x "neo4j" > /dev/null; then
    echo "✅ Neo4j is running"
else
    echo "❌ Neo4j is not running"
    echo "   Start Neo4j with: neo4j start"
    echo ""
    read -p "Do you want to start Neo4j now? (y/n): " start_neo4j
    if [ "$start_neo4j" = "y" ]; then
        neo4j start
        sleep 3
    else
        echo "⚠️  Warning: Neo4j must be running for the pipeline to work!"
    fi
fi

echo ""
echo "🧪 Testing parser with existing results..."
python3 test_parsing.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Parser test successful!"
    echo ""
    echo "🌐 Starting Flask web server..."
    echo "   Access at: http://localhost:5000"
    echo "   Test endpoint: http://localhost:5000/test-parse"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    python3 app.py
else
    echo ""
    echo "❌ Parser test failed!"
    echo "   Check the error messages above"
    exit 1
fi

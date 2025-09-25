#!/bin/bash

# Run tests with coverage reporting
# This script mimics what the GitHub Action does for local development

echo "🧪 Running tests with coverage..."

# Ensure PYTHONPATH is set
export PYTHONPATH=.

# Run pytest with coverage
pytest --cov=app \
       --cov-report=xml \
       --cov-report=html \
       --cov-report=term-missing \
       -v

# Check if coverage was generated
if [ -f "coverage.xml" ]; then
    echo "✅ Coverage XML report generated: coverage.xml"
fi

if [ -d "htmlcov" ]; then
    echo "✅ Coverage HTML report generated: htmlcov/index.html"
    echo "📊 Open htmlcov/index.html in your browser to view detailed coverage"
fi

echo "🎉 Tests completed!"
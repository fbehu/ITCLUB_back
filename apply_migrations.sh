#!/bin/bash

# Script to apply migrations on the production server
# Usage: ./apply_migrations.sh

set -e  # Exit on error

echo "=========================================="
echo "ITCLUB Backend - Migration Script"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please create it first: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q psycopg2-binary

# Run migrations
echo "🔄 Running migrations..."
python manage.py migrate

# Show migration status
echo ""
echo "✅ Checking migration status..."
python manage.py showmigrations chat

echo ""
echo "=========================================="
echo "✓ Migrations completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Restart your Django application"
echo "2. Test the API endpoints"
echo ""
echo "For gunicorn:"
echo "  sudo systemctl restart gunicorn"
echo ""
echo "For supervisor:"
echo "  sudo supervisorctl restart gunicorn"
echo ""
echo "For docker:"
echo "  docker-compose restart web"
echo ""

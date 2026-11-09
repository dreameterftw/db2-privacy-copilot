#!/bin/bash
# Setup script for Db2 Privacy Copilot
# This script sets up the development environment on Unix-like systems

set -e

echo "========================================"
echo "Db2 Privacy Copilot - Setup Script"
echo "========================================"
echo

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "✓ .env created"
    echo
    echo "⚠️  IMPORTANT: Edit .env and set a strong DB2_PASSWORD"
    echo
else
    echo "✓ .env already exists"
fi

# Create Python virtual environment
if [ ! -d .venv ]; then
    echo "Creating Python virtual environment..."
    python3.11 -m venv .venv || python3 -m venv .venv || python -m venv .venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate || . .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -e ".[dev]"
echo "✓ Dependencies installed"

echo
echo "========================================"
echo "Setup complete!"
echo "========================================"
echo
echo "Next steps:"
echo "  1. Edit .env and set DB2_PASSWORD"
echo "  2. Start Db2: docker compose up -d"
echo "  3. Wait for Db2 to initialize (5-10 minutes)"
echo "     Check status: docker compose logs -f db2"
echo "     Look for: 'Setup has completed'"
echo "  4. Initialize database: python app/bootstrap.py"
echo "  5. Seed data: python eval/seed.py"
echo "  6. Run tests: pytest"
echo

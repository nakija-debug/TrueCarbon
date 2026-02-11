#!/bin/bash

# TrueCarbon Project - Local Setup Script
# This script sets up and runs the TrueCarbon project locally

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        TrueCarbon Project - Local Setup Script               ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "📦 Checking Python version..."
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "   Python: $PYTHON_VERSION"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo "🔧 Creating virtual environment..."
    cd "$BACKEND_DIR"
    python -m venv venv
    echo "   ✓ Virtual environment created"
else
    echo "   ✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🚀 Activating virtual environment..."
source "$BACKEND_DIR/venv/bin/activate"
echo "   ✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
echo "   ✓ pip upgraded"
echo ""

# Install requirements
echo "📦 Installing dependencies..."
cd "$BACKEND_DIR"
pip install -r requirements.txt > /dev/null 2>&1
echo "   ✓ Dependencies installed"
echo ""

# Setup environment file
echo "⚙️  Setting up environment configuration..."
if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo "   Creating .env from .env.example..."
    cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
    
    # Generate SECRET_KEY if openssl is available
    if command -v openssl &> /dev/null; then
        SECRET_KEY=$(openssl rand -hex 32)
        sed -i "s/your-secret-key-here-generate-with-openssl-rand-hex-32/$SECRET_KEY/" "$BACKEND_DIR/.env"
        echo "   ✓ Generated SECRET_KEY"
    fi
    echo "   ✓ .env file created"
else
    echo "   ✓ .env file already exists"
fi
echo ""

# Setup database
echo "💾 Setting up database..."
cd "$BACKEND_DIR"

# Create database file for SQLite (default)
if grep -q "sqlite+aiosqlite" .env; then
    echo "   Using SQLite (aiosqlite)"
    echo "   ✓ Database will be created on first run"
elif grep -q "postgresql" .env; then
    echo "   Using PostgreSQL"
    echo "   Make sure PostgreSQL is running and accessible"
    echo "   ⚠️  Update DATABASE_URL in .env if needed"
fi
echo ""

# Initialize database with Alembic
echo "🗄️  Initializing database schema..."
cd "$BACKEND_DIR"
if [ -d "alembic/versions" ]; then
    alembic upgrade head > /dev/null 2>&1 || true
    echo "   ✓ Database schema initialized"
else
    echo "   ⚠️  Alembic migrations not found"
fi
echo ""

# Verify imports
echo "✅ Verifying imports..."
cd "$BACKEND_DIR"
python -c "from app.main import app; print('   ✓ FastAPI app imports successfully')" || {
    echo "   ✗ Error importing app"
    exit 1
}
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    Setup Complete! ✓                          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Show next steps
echo "📋 Next Steps:"
echo ""
echo "1️⃣  Start the backend API server:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "2️⃣  API Documentation (once server is running):"
echo "   • Swagger UI: http://localhost:8000/docs"
echo "   • ReDoc: http://localhost:8000/redoc"
echo ""
echo "3️⃣  (Optional) Start the frontend:"
echo "   cd frontend/true_carbon"
echo "   npm install"
echo "   npm run dev"
echo ""
echo "📝 Configuration:"
echo "   • Backend: $BACKEND_DIR/.env"
echo "   • Database: Check DATABASE_URL setting"
echo "   • API Prefix: /api/v1"
echo ""
echo "🔗 API Base URL: http://localhost:8000"
echo "📚 Documentation: http://localhost:8000/docs"
echo ""

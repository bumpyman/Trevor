#!/bin/bash
# Setup script for Trevor Bot 2.0

set -e  # Exit on error

echo "🤖 Trevor Bot 2.0 - Setup Script"
echo "================================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.10+ is required. Current version: $python_version"
    exit 1
fi
echo "✅ Python $python_version detected"
echo ""

# Check Docker
echo "📋 Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi
echo "✅ Docker detected"
echo ""

# Check Docker Compose
echo "📋 Checking Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    echo "⚠️  docker-compose not found. Trying 'docker compose'..."
    if ! docker compose version &> /dev/null; then
        echo "❌ Docker Compose is not installed."
        exit 1
    fi
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi
echo "✅ Docker Compose detected"
echo ""

# Create virtual environment
echo "🐍 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✅ pip upgraded"
echo ""

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your credentials:"
    echo "   - TELEGRAM_BOT_TOKEN (get from @BotFather)"
    echo "   - ANTHROPIC_API_KEY (get from console.anthropic.com)"
    echo "   - SENDGRID_API_KEY (get from sendgrid.com)"
    echo "   - HUG_HEMATOLOGY_EMAIL"
    echo "   - FROM_EMAIL"
    echo ""
else
    echo "ℹ️  .env file already exists"
    echo ""
fi

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p logs
echo "✅ Logs directory created"
echo ""

# Start Docker services
echo "🐳 Starting Docker services (PostgreSQL + HAPI FHIR)..."
$DOCKER_COMPOSE up -d
echo "✅ Docker services started"
echo ""

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5

# Test database connection
echo "🔍 Testing database connection..."
python3 -c "from src.models.database import init_db; init_db(); print('✅ Database initialized successfully')" || {
    echo "❌ Database initialization failed"
    exit 1
}
echo ""

# Test FHIR server
echo "🔍 Testing FHIR server..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -sf http://localhost:8080/fhir/metadata > /dev/null 2>&1; then
        echo "✅ FHIR server is ready"
        break
    fi
    attempt=$((attempt + 1))
    if [ $attempt -eq $max_attempts ]; then
        echo "⚠️  FHIR server is not responding yet. It may still be starting up."
        echo "   You can check status with: docker logs trevor-fhir"
    else
        sleep 2
    fi
done
echo ""

# Summary
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python main.py"
echo ""
echo "Useful commands:"
echo "  - Start services: $DOCKER_COMPOSE up -d"
echo "  - Stop services: $DOCKER_COMPOSE down"
echo "  - View logs: docker logs trevor-postgres"
echo "  - View FHIR logs: docker logs trevor-fhir"
echo ""
echo "Documentation: README.md"
echo ""

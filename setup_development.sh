#!/bin/bash

echo "🚀 Setting up Cognee Development Environment..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required but not installed."
    exit 1
fi

# Install required dependencies for GUI
echo "📦 Installing GUI dependencies..."
pip install PySide6 qasync python-dotenv

# Create .env file from template if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️ Creating .env file..."
    cat > .env << 'EOF'
# Embedding Configuration for Hugging Face
EMBEDDING_PROVIDER=fastembed
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
EMBEDDING_API_KEY=your_huggingface_api_key_here
EMBEDDING_DIMENSIONS=384
HUGGINGFACE_TOKENIZER=sentence-transformers/all-MiniLM-L6-v2

# LLM Configuration for OpenRouter
LLM_PROVIDER=custom
LLM_MODEL=openrouter/google/gemini-2.5-flash-preview-05-20
LLM_ENDPOINT=https://openrouter.ai/api/v1/chat/completions
LLM_API_KEY=your_openrouter_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_API_BASE=https://openrouter.ai/api/v1
EOF
    echo "📝 .env file created. Please update it with your API keys!"
    echo "   - Add your OpenRouter API key"
    echo "   - Add your HuggingFace API key"
else
    echo "✅ .env file already exists"
fi

# Check if virtual environment is active
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Warning: No virtual environment detected"
    echo "   Consider using: python -m venv .venv && source .venv/bin/activate"
fi

echo ""
echo "🎉 Setup completed!"
echo ""
echo "📋 Next steps:"
echo "   1. Update .env file with your API keys"
echo "   2. Run: python cognee-gui.py"
echo ""
echo "🔗 API endpoints available at: http://localhost:8000"
echo "📚 Swagger docs: http://localhost:8000/docs" 
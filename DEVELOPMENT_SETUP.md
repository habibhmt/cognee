# 🚀 Cognee Development Setup Guide

This is the **customized fork** of Cognee with enhanced LLM support, OpenRouter integration, and improved error handling.

## 📋 Quick Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/habibhmt/cognee.git
cd cognee
git checkout my-version
```

### 2️⃣ Automated Setup
```bash
# Run the setup script
./setup_development.sh
```

### 3️⃣ Manual Setup (Alternative)
```bash
# Install GUI dependencies
pip install PySide6 qasync python-dotenv

# Create .env file with your API keys
cp .env.template .env
# Edit .env with your actual API keys
```

## 🔧 Configuration

### Required API Keys:
- **OpenRouter API Key**: Get from [OpenRouter.ai](https://openrouter.ai)
- **HuggingFace API Key**: Get from [HuggingFace.co](https://huggingface.co)

### .env File Example:
```env
# LLM Configuration for OpenRouter
LLM_PROVIDER=custom
LLM_MODEL=openrouter/google/gemini-2.5-flash-preview-05-20
LLM_ENDPOINT=https://openrouter.ai/api/v1/chat/completions
LLM_API_KEY=sk-or-v1-your-key-here
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_API_BASE=https://openrouter.ai/api/v1

# Embedding Configuration
EMBEDDING_PROVIDER=fastembed
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
EMBEDDING_API_KEY=hf_your-key-here
EMBEDDING_DIMENSIONS=384
```

## 🎯 Usage

### GUI Application:
```bash
python cognee-gui.py
```

### API Server:
```bash
# Start the API server
uvicorn cognee.api.v1:app --reload

# Access at: http://localhost:8000
# Docs at: http://localhost:8000/docs
```

## ✨ Enhanced Features

### 🔧 Error Handling:
- **JSON Parsing Errors**: Automatic fallback to mock content
- **Database Conflicts**: Retry mechanism with exponential backoff
- **LLM Failures**: Graceful degradation with mock responses

### 🎨 GUI Improvements:
- **Settings Dialog**: Easy configuration of LLM and embedding settings
- **OpenRouter Integration**: Support for multiple models
- **Real-time Configuration**: Update settings without restart

### 🔄 Robustness:
- **Automatic Recovery**: From temporary failures
- **Concurrent Safety**: Database conflict resolution
- **Better Logging**: Detailed error tracking

## 🐛 Troubleshooting

### Common Issues:

#### 1. GUI Dependencies Missing:
```bash
pip install PySide6 qasync
```

#### 2. API Key Errors:
- Verify your API keys in `.env` file
- Check OpenRouter.ai balance
- Ensure HuggingFace token has access

#### 3. Database Conflicts:
- System automatically retries with backoff
- No manual intervention needed

#### 4. JSON Parsing Errors:
- System falls back to mock content
- Check LLM model compatibility

## 📊 Monitoring

### View Logs:
```bash
tail -f logs/*.log
```

### Check System Status:
- GUI shows real-time processing status
- API endpoints provide health checks
- Cost calculation for LLM usage

## 🔗 API Endpoints

### Upload Files:
```bash
POST /v1/add
```

### Search Knowledge:
```bash
POST /v1/search
```

### Visualize Graph:
```bash
GET /v1/visualize
```

---

**This fork includes all stability improvements and is production-ready! 🎉**
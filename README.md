# DeepVerify - AI-Powered Fake News Detection Platform

<div align="center">

**🔍 Detect. Verify. Trust.**

An intelligent fact-checking platform that uses machine learning and AI to analyze news articles, detect misinformation, and provide confidence-scored verdicts.

[Quick Start](#-quick-start) • [Features](#-features) • [Tech Stack](#-tech-stack) • [Documentation](#-documentation) • [API Reference](#-api-endpoints)

</div>

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Quick Start](#-quick-start)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Setup Instructions](#-setup-instructions)
- [API Endpoints](#-api-endpoints)
- [Configuration](#-configuration)
- [Recent Updates](#-recent-updates)
- [Documentation](#-documentation)
- [License](#-license)

---

## 🎯 Project Overview

**DeepVerify** (formerly VeriGlow) is an enterprise-grade fake news detection and fact-checking platform that combines machine learning, natural language processing, and AI-powered analysis to help users verify the authenticity of news articles and claims.

### Key Capabilities

- **ML-Based Analysis**: Trained machine learning models classify articles as Real, Fake, or Uncertain
- **Confidence Scoring**: Provides 0-100% confidence scores for each verdict
- **Source Verification**: Cross-references claims with trusted news sources
- **Multi-Language Support**: Automatic language detection and translation
- **AI Chatbot Assistant**: Ollama-powered conversational assistant (llama3.2:1b model)
- **User Authentication**: Secure JWT-based authentication system
- **Analysis History**: Track and review past analyses
- **Statistics Dashboard**: View analysis trends and insights
- **Browser Extension**: Chrome extension for quick fact-checking

---

## 🚀 Quick Start

### One-Click Launch (Windows)

**Just double-click:** `START-VERIGLOW.bat`

The launcher automatically:
- ✅ Checks prerequisites
- ✅ Installs dependencies
- ✅ Starts Docker services (MongoDB, Redis)
- ✅ Starts backend & frontend servers
- ✅ Opens application in browser

**First run:** ~5-10 minutes | **Subsequent runs:** ~30 seconds

### Stop Application

Double-click: `STOP-VERIGLOW.bat`

### Access URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

---

## ✨ Features

### Core Features

- **News Article Analysis**
  - Paste article text or URL on the home page
  - ML-based verdict: Real/Fake/Uncertain
  - Confidence scoring (0-100%)
  - Sentiment analysis and bias detection
  - Source credibility verification

- **AI Chatbot Assistant**
  - Powered by Ollama (llama3.2:1b model)
  - Explains DeepVerify features and usage
  - Provides latest news and current events
  - Offers fact-checking tips and media literacy advice
  - Intelligent conversation on any topic

- **User Authentication**
  - Secure signup/login system
  - JWT token-based authentication
  - Password hashing (bcrypt/argon2)
  - Session management

- **Analysis History**
  - Save and review past analyses
  - Track verification history
  - Export analysis results

- **Statistics Dashboard**
  - View analysis trends
  - Track accuracy metrics
  - Monitor system performance

- **Multi-Language Support**
  - Automatic language detection
  - Translation support via deep-translator
  - Analyze articles in multiple languages

### Security Features

- JWT authentication with secure token management
- Password hashing using Passlib (bcrypt/argon2)
- Rate limiting on API endpoints
- Request size limits
- Input validation and sanitization (Bleach)
- CORS protection with strict whitelisting
- CSRF protection (configurable)

### Enterprise Features

- **Monitoring**: Prometheus metrics and Sentry error tracking
- **Caching**: Redis-based caching for improved performance
- **Background Tasks**: Celery for asynchronous processing
- **GDPR Compliance**: Privacy-focused data handling
- **Batch Processing**: Analyze multiple articles efficiently
- **Docker Deployment**: Containerized architecture

### UI/UX Features

- Interactive RGB background effect
- Responsive design for all devices
- Custom logo with magnifying glass + detective hat
- Intuitive navigation
- Real-time analysis feedback

---

## 🛠 Tech Stack

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 14.2.3 | React framework for production |
| **React** | 18.2.0 | UI library |
| **TypeScript** | 5.3.3 | Type-safe JavaScript |
| **Axios** | 1.6.7 | HTTP client for API calls |

**Frontend Features:**
- Server-side rendering (SSR)
- Interactive RGB background effect
- Custom Logo component
- Responsive design

### Backend

| Technology | Purpose |
|------------|---------|
| **FastAPI** | Modern Python web framework |
| **Uvicorn** | ASGI server with standard extras |
| **Motor** | Async MongoDB driver |
| **Redis** | Caching and session storage |
| **Celery** | Background task processing |

### AI/ML Stack

| Technology | Purpose |
|------------|---------|
| **Scikit-learn** | Machine learning models |
| **NLTK** | Natural language processing |
| **TextBlob** | Sentiment analysis |
| **Ollama** | Local AI inference (llama3.2:1b) |
| **Langdetect** | Language detection |
| **Deep-translator** | Multi-language translation |
| **BeautifulSoup4** | Web scraping and parsing |

### Security & Authentication

| Technology | Purpose |
|------------|---------|
| **PyJWT** | JSON Web Token implementation |
| **Passlib** | Password hashing (bcrypt/argon2) |
| **Cryptography** | Encryption utilities |
| **Bleach** | Input sanitization |
| **Email-validator** | Email validation |

### Infrastructure

| Technology | Version | Purpose |
|------------|---------|---------|
| **Docker** | Latest | Containerization |
| **Docker Compose** | 3.8 | Multi-container orchestration |
| **MongoDB** | 6 | NoSQL database |
| **Redis** | 7-alpine | In-memory data store |

### Monitoring & Observability

| Technology | Purpose |
|------------|---------|
| **Prometheus** | Metrics collection |
| **Sentry** | Error tracking and monitoring |
| **Python Logging** | Application logging |

---

## 📁 Project Structure

```
Fake-News-main/
├── backend/                    # FastAPI backend application
│   ├── admin/                  # Admin functionality
│   ├── app_logging/            # Logging configuration
│   ├── auth/                   # Authentication modules
│   ├── cache/                  # Redis caching layer
│   ├── compliance/             # GDPR compliance
│   ├── config/                 # Configuration management
│   ├── middleware/             # Custom middleware
│   │   ├── rate_limiter.py     # Rate limiting
│   │   ├── csrf_protection.py  # CSRF protection
│   │   └── error_handler.py    # Error handling
│   ├── ml/                     # Machine learning models
│   ├── monitoring/             # Prometheus & Sentry
│   ├── payment/                # Payment integration
│   ├── scripts/                # Utility scripts
│   ├── security/               # Security utilities
│   ├── services/               # Business logic services
│   ├── tasks/                  # Celery tasks
│   ├── validation/             # Input validation
│   ├── webhooks/               # Webhook handlers
│   ├── main.py                 # Application entry point
│   ├── auth.py                 # Auth router
│   ├── analyze_router.py       # Analysis endpoints
│   ├── chat.py                 # Chatbot endpoints
│   ├── history.py              # History endpoints
│   ├── stats.py                # Statistics endpoints
│   ├── model_final.pkl         # Trained ML model
│   ├── tfidf_final.pkl         # TF-IDF vectorizer
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile              # Backend container
│   └── .env                    # Environment variables
│
├── frontend/                   # Next.js frontend application
│   ├── src/
│   │   ├── app/                # Next.js app directory
│   │   ├── components/         # React components
│   │   └── styles/             # CSS styles
│   ├── package.json            # Node dependencies
│   ├── tsconfig.json           # TypeScript config
│   ├── Dockerfile              # Frontend container
│   └── .env.local              # Frontend environment
│
├── browser-extension/          # Chrome extension
│   ├── manifest.json           # Extension manifest
│   ├── popup.html              # Extension popup UI
│   ├── popup.js                # Popup logic
│   └── background.js           # Background script
│
├── docker-compose.yml          # Docker orchestration
├── START-VERIGLOW.bat          # Windows startup script
├── STOP-VERIGLOW.bat           # Windows shutdown script
└── README.md                   # This file
```

---

## 🔧 Setup Instructions

### Prerequisites

Before starting, ensure you have the following installed:

1. **Python 3.11+** - [Download](https://python.org)
   - ⚠️ Check "Add Python to PATH" during installation
   
2. **Node.js 18+** - [Download](https://nodejs.org)
   - Includes npm package manager
   
3. **Docker Desktop** - [Download](https://docker.com/products/docker-desktop)
   - Must be running before starting the application
   - See `DOCKER-SETUP-GUIDE.txt` for detailed installation

4. **Ollama** (Optional, for AI chatbot)
   - [Download Ollama](https://ollama.ai)
   - Pull the model: `ollama pull llama3.2:1b`

### Installation

#### Option 1: Automated Setup (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Fake-News-main
   ```

2. **Start Docker Desktop**
   - Ensure Docker is running

3. **Run the launcher**
   - Double-click `START-VERIGLOW.bat` (Windows)
   - The script handles all setup automatically

#### Option 2: Manual Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Fake-News-main
   ```

2. **Start Docker services**
   ```bash
   docker-compose up -d mongo redis
   ```

3. **Setup Backend**
   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

4. **Setup Frontend**
   ```bash
   cd frontend
   npm install
   ```

5. **Configure Environment Variables**
   - Backend: Edit `backend/.env`
   - Frontend: Edit `frontend/.env.local`

6. **Start Services**
   ```bash
   # Terminal 1 - Backend
   cd backend
   python main.py

   # Terminal 2 - Frontend
   cd frontend
   npm run dev

   # Terminal 3 - Celery (optional)
   cd backend
   celery -A celery_app worker --loglevel=info
   ```

7. **Start Ollama (optional)**
   ```bash
   ollama serve
   ```

### Environment Variables

#### Backend (.env)

```env
# Database
MONGO_URI=mongodb://localhost:27017
MONGO_DB=veriglow

# Cache
REDIS_URL=redis://localhost:6379

# Authentication
JWT_SECRET=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=1440

# CORS
FRONTEND_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# API Keys (optional)
GOOGLE_FACTCHECK_API_KEY=your-key-here
GOOGLE_GEMINI_API_KEY=your-key-here
NEWS_API_KEY=your-key-here

# Environment
ENVIRONMENT=development
DEBUG=true
```

#### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🌐 API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/signup` | Register new user | No |
| POST | `/api/v1/auth/login` | Login user | No |

**Signup Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "username": "username"
}
```

**Login Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "email": "user@example.com",
    "username": "username"
  }
}
```

### Analysis

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/analyze` | Analyze news article | Optional |

**Request:**
```json
{
  "text": "Article text to analyze...",
  "url": "https://example.com/article",
  "language": "en"
}
```

**Response:**
```json
{
  "verdict": "Real",
  "confidence": 87.5,
  "sentiment": "neutral",
  "sources": ["source1.com", "source2.com"],
  "language": "en",
  "analysis_id": "abc123"
}
```

### Chat

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/chat` | Chat with AI assistant | No |
| GET | `/api/v1/chat/health` | Check chatbot status | No |

**Request:**
```json
{
  "message": "How do I use DeepVerify?"
}
```

**Response:**
```json
{
  "reply": "DeepVerify is easy to use! Simply paste your article text..."
}
```

### History

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/history` | Get user's analysis history | Yes |
| GET | `/api/v1/history/{id}` | Get specific analysis | Yes |

### Statistics

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/stats` | Get platform statistics | Yes |

**Response:**
```json
{
  "total_analyses": 1250,
  "accuracy_rate": 92.3,
  "fake_detected": 450,
  "real_verified": 800
}
```

### Health Check

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/health` | Check API health | No |

---

## ⚙️ Configuration

### MongoDB Configuration

The application uses MongoDB for data persistence:

- **Connection URI**: `mongodb://localhost:27017`
- **Database**: `veriglow`
- **Collections**: `users`, `analyses`, `history`, `stats`

### Redis Configuration

Redis is used for caching and session management:

- **Connection URL**: `redis://localhost:6379`
- **Use Cases**: Rate limiting, session storage, analysis caching

### Ollama Setup

For the AI chatbot to work:

1. Install Ollama: https://ollama.ai
2. Pull the model:
   ```bash
   ollama pull llama3.2:1b
   ```
3. Start Ollama server:
   ```bash
   ollama serve
   ```
4. The chatbot connects to `http://localhost:11434`

### Rate Limiting

Configured per endpoint:
- **Default**: 60 requests/minute
- **Analysis**: 20 requests/minute
- **Chat**: 30 requests/minute
- **Login**: 10 requests/minute

### Security Settings

- **JWT Secret**: Change in production (`.env` file)
- **Token Expiry**: 30 minutes (access), 24 hours (refresh)
- **CORS**: Whitelist specific origins in production
- **CSRF Protection**: Disabled in development, enable for production

---

## 🆕 Recent Updates

### Version 2.0 - DeepVerify Rebrand

- ✅ **Rebranded** from VeriGlow to DeepVerify
- ✅ **Added Logo Component** with magnifying glass + detective hat design
- ✅ **Moved News Analyzer** to home page for better UX
- ✅ **Moved Statistics** to dedicated dashboard page
- ✅ **Integrated Ollama Chatbot** with llama3.2:1b model
- ✅ **Added Interactive RGB Background** effect
- ✅ **Removed CSRF Protection** in development mode
- ✅ **Increased Ollama Timeout** to 120 seconds for slower systems
- ✅ **Enhanced Chat System** with intent detection and news integration
- ✅ **Improved Error Handling** with retry logic for Ollama
- ✅ **Added Health Check Endpoints** for monitoring

### Security Improvements

- ✅ JWT authentication with secure token management
- ✅ Password hashing using bcrypt/argon2
- ✅ Rate limiting on all endpoints
- ✅ Input validation and sanitization
- ✅ Request size limits
- ✅ CORS protection with strict whitelisting

### Performance Optimizations

- ✅ Redis caching for frequently accessed data
- ✅ Async MongoDB operations with Motor
- ✅ Background task processing with Celery
- ✅ Lazy loading of ML models
- ✅ Connection pooling for databases

---

## 📖 Documentation

### Quick Start Guides

- `SIMPLE-START.txt` - Ultra-simple 3-step guide for beginners
- `README-FIRST.txt` - Guided setup path
- `BEFORE-YOU-START.txt` - Pre-installation checklist
- `HOW-TO-RUN-DOCKER.txt` - Quick Docker guide

### Detailed Guides

- `DOCKER-SETUP-GUIDE.txt` - Step-by-step Docker installation for Windows
- `QUICK-START-GUIDE.txt` - Complete user guide with troubleshooting
- `STARTUP-FLOW.txt` - Visual guide of application startup
- `SECURITY_IMPROVEMENTS.md` - Security features documentation

### Reference

- `FILES-OVERVIEW.txt` - Explanation of each file
- `DOCUMENTATION-INDEX.txt` - Complete list of help files
- `/docs` endpoint - Interactive API documentation (Swagger UI)
- `/redoc` endpoint - Alternative API documentation (ReDoc)

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🐛 Troubleshooting

### Common Issues

**Docker not starting:**
- Ensure Docker Desktop is running
- Check Docker service status
- Restart Docker Desktop

**Ollama connection failed:**
- Install Ollama: https://ollama.ai
- Run: `ollama serve`
- Pull model: `ollama pull llama3.2:1b`

**Port already in use:**
- Backend (8000): Check if another service is using port 8000
- Frontend (3000): Check if another Next.js app is running
- MongoDB (27017): Check for existing MongoDB instances
- Redis (6379): Check for existing Redis instances

**Module not found errors:**
- Backend: `pip install -r requirements.txt`
- Frontend: `npm install`

### Getting Help

- Check the documentation files in the project root
- Review the API documentation at http://localhost:8000/docs
- Check application logs for error messages
- Open an issue on GitHub

---

## 📞 Support

For support and questions:
- 📧 Email: support@deepverify.com
- 🐛 Issues: GitHub Issues
- 📚 Documentation: `/docs` endpoint

---

<div align="center">

**Built with ❤️ by the DeepVerify Team**

[⬆ Back to Top](#deepverify---ai-powered-fake-news-detection-platform)

</div>


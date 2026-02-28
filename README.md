# DeepVerify

> Can you trust what you're reading? DeepVerify helps you find out.

Misinformation spreads fast. DeepVerify is a tool I built to slow it down — paste in any news article or URL and get an instant verdict on whether it's likely real, fake, or somewhere in between. It uses a trained ML model under the hood, but the goal was always simple: make fact-checking fast and accessible for everyone.

---

## What it does

At its core, DeepVerify analyzes news articles and returns a verdict with a confidence score. But there's more to it:

- **Paste text or a URL** — the analyzer lives right on the home page, no digging around
- **Get a verdict in seconds** — Real, Fake, or Uncertain, with a 0-100% confidence score
- **See the reasoning** — sentiment analysis, bias signals, and source credibility checks
- **Ask the chatbot** — an Ollama-powered assistant (llama3.2:1b) that can explain results, give media literacy tips, or just chat
- **Track your history** — logged-in users can review every article they've checked
- **Use it in your browser** — there's a Chrome extension for quick checks while you browse
- **Read in any language** — automatic language detection and translation built in

---

## Getting started

### The easy way (Windows)

Just double-click `START-VERIGLOW.bat`. It checks your prerequisites, installs what's missing, spins up Docker, and opens the app in your browser automatically.

- First run: around 5-10 minutes (downloading dependencies)
- After that: around 30 seconds

To stop everything: double-click `STOP-VERIGLOW.bat`.

### The manual way

Prerequisites: Python 3.11+, Node.js 18+, Docker Desktop

```bash
# 1. Clone the repo
git clone <repository-url>
cd Fake-News-main

# 2. Start the databases
docker-compose up -d mongo redis

# 3. Set up the backend
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux
pip install -r requirements.txt

# 4. Set up the frontend
cd ../frontend
npm install

# 5. Start everything
# Terminal 1
cd backend && python main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
# If the above fails, try:
npx next dev
```

Then open http://localhost:3000 and you're good to go.

Want the AI chatbot? Install Ollama (https://ollama.ai), run `ollama pull llama3.2:1b`, then `ollama serve`.

---

## Environment setup

**backend/.env**
```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB=veriglow
REDIS_URL=redis://localhost:6379

JWT_SECRET=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=1440

FRONTEND_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Optional but recommended
GOOGLE_FACTCHECK_API_KEY=your-key-here
NEWS_API_KEY=your-key-here

ENVIRONMENT=development
DEBUG=true
```

**frontend/.env.local**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Tech stack

**Frontend:** Next.js 14, React 18, TypeScript, Axios

**Backend:** FastAPI, Uvicorn, Motor (async MongoDB), Redis, Celery

**ML / NLP:** Scikit-learn, NLTK, TextBlob, Langdetect, Deep-translator, BeautifulSoup4

**AI Chatbot:** Ollama (llama3.2:1b running locally)

**Infrastructure:** Docker, MongoDB 6, Redis 7

**Security:** PyJWT, Passlib (bcrypt/argon2), Bleach, rate limiting, CORS whitelisting

---

## API overview

The full interactive docs are at http://localhost:8000/docs once the app is running. Here's the quick summary:

| Endpoint | Method | What it does |
|---|---|---|
| `/api/v1/auth/signup` | POST | Create an account |
| `/api/v1/auth/login` | POST | Log in, get a JWT |
| `/api/v1/analyze` | POST | Analyze an article |
| `/api/v1/chat` | POST | Chat with the assistant |
| `/api/v1/history` | GET | Your past analyses |
| `/api/v1/stats` | GET | Platform statistics |
| `/health` | GET | Health check |

Quick example — analyze an article:
```json
POST /api/v1/analyze
{
  "text": "Article text here...",
  "url": "https://example.com/article"
}

Response:
{
  "verdict": "Real",
  "confidence": 87.5,
  "sentiment": "neutral",
  "sources": ["source1.com", "source2.com"]
}
```

---

## Project layout

```
Fake-News-main/
├── backend/          # FastAPI app — ML models, auth, API routes
├── frontend/         # Next.js app — UI, components, styles
├── browser-extension/# Chrome extension for in-browser checks
├── docker-compose.yml
├── START-VERIGLOW.bat
└── STOP-VERIGLOW.bat
```

---

## Troubleshooting

**Docker won't start** — Make sure Docker Desktop is actually open and running before launching.

**Chatbot not responding** — Run `ollama serve` in a separate terminal and make sure you've pulled the model (`ollama pull llama3.2:1b`).

**Port conflict** — Something else is using 3000, 8000, 27017, or 6379. Check your running processes and stop whatever's occupying those ports.

**Missing packages** — Run `pip install -r requirements.txt` (backend) or `npm install` (frontend) again.

**Frontend won't start with npm run dev** — Try `npx next dev` instead as a fallback.

Still stuck? Check the logs or open an issue on GitHub (https://github.com/AKNIAZI47/DeepVerify/issues).

---

## Contributing

Found a bug or have an idea? Contributions are welcome.

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-idea`
3. Make your changes and commit: `git commit -m 'Add your idea'`
4. Push and open a Pull Request

---

## License

MIT — do whatever you want with it, just don't blame me if it breaks.

---

Built by AKNIAZI47 (https://github.com/AKNIAZI47)
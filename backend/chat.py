from fastapi import APIRouter, Depends
from pydantic import BaseModel
import requests
import logging
import time
from dependencies import get_app_settings
from config.settings import Settings

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

# Logging setup
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

class ChatIn(BaseModel):
    message: str

class ChatOut(BaseModel):
    reply: str

SYSTEM_PROMPT = """You are DeepVerify Assistant, a professional and friendly AI assistant for the DeepVerify fact-checking platform.

ABOUT DEEPVERIFY:
- DeepVerify is an AI-powered fact-checking platform that analyzes news articles and text for accuracy
- Core Features:
  * Text/URL Analysis: Users paste article text or URLs on the home page and click "Analyze"
  * Verdicts: System provides True/False/Partially True/Misleading with confidence scores (0-100%)
  * Source Verification: Cross-references claims with trusted news sources
  * Sentiment Analysis: Detects emotional language and bias in articles
  * History Tracking: Logged-in users can save and review their analysis history
  * ML-Based Scoring: Uses machine learning models trained on fact-checking datasets
  * Authentication: Secure login/signup system
  
BEST PRACTICES FOR USERS:
- Paste full article text, not just headlines (headlines often lack context)
- Avoid sending personal/sensitive information
- Check the confidence meter - higher % = more reliable verdict
- Review the source citations provided with results
- Use for news verification, claim checking, and research

YOUR CAPABILITIES:
1. ✅ Explain how to use DeepVerify features
2. ✅ Discuss analysis results, verdicts, and confidence scores
3. ✅ Provide latest news and current events
4. ✅ Have intelligent conversations on any topic
5. ✅ Offer fact-checking tips and media literacy advice
6. ✅ Answer technical questions about how the system works

COMMUNICATION STYLE:
- Be friendly, professional, and concise
- Use emojis sparingly but appropriately
- Provide balanced perspectives on news
- Cite sources when discussing news
- If unsure about something, say so honestly
- Always prioritize user privacy and security

Remember: You're helping users verify information in a world of misinformation. Be accurate, helpful, and trustworthy."""

def fetch_latest_news(query: str = None, settings: Settings = None) -> str:
    """Fetch latest news from NewsAPI"""
    try:
        if not settings or not settings.news_api_key:
            return ""
        
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": 5,
            "apiKey": settings.news_api_key.strip(),
        }
        
        if query and query.lower() not in ["today", "news", "latest"]:
            params["q"] = query
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            articles = response.json().get("articles", [])
            if not articles:
                return ""
            
            news_text = "**📰 Today's Top News Headlines:**\n\n"
            for i, article in enumerate(articles[:5], 1):
                news_text += f"{i}. **{article.get('title', 'N/A')}**\n"
                news_text += f"   Source: {article.get('source', {}).get('name', 'Unknown')} | "
                news_text += f"{article.get('publishedAt', '')[:10]}\n"
                if article.get("description"):
                    news_text += f"   {article['description'][:150]}...\n"
                news_text += "\n"
            return news_text
        else:
            logger.warning("NewsAPI non-200: %s %s", response.status_code, response.text[:200])
            return ""
    except Exception as e:
        logger.error("NewsAPI fetch failed: %s", e, exc_info=True)
        return ""

def detect_intent(message: str) -> str:
    """Detect the primary intent of the user's message"""
    msg_lower = message.lower()
    
    news_keywords = ["news", "latest", "today", "current", "trending", "happening",
                     "breaking", "headlines", "events", "world", "politics", "sports",
                     "technology", "business", "entertainment"]
    if any(keyword in msg_lower for keyword in news_keywords):
        return "news"
    
    app_keywords = ["how", "use", "work", "tutorial", "guide", "help", "feature",
                    "explain", "verdict", "score", "accuracy", "confidence", "analyze",
                    "history", "login", "save", "privacy", "security", "algorithm"]
    if any(keyword in msg_lower for keyword in app_keywords):
        return "app_help"
    
    factcheck_keywords = ["verify", "check", "true", "false", "claim", "fact check",
                          "misinformation", "disinformation", "fake", "credible",
                          "misleading", "bias", "source"]
    if any(keyword in msg_lower for keyword in factcheck_keywords):
        return "factcheck"
    
    return "general"

async def generate_response_ollama(user_message: str, intent: str, settings: Settings) -> str:
    """Generate response using Ollama (local AI)"""
    try:
        context = ""
        if intent == "news":
            news_data = fetch_latest_news(user_message, settings)
            if news_data:
                context = f"\n\nHere is current news context to reference:\n{news_data}"
        elif intent == "app_help":
            context = "\n\nUser is asking about DeepVerify features. Provide detailed, step-by-step explanations."
        elif intent == "factcheck":
            context = "\n\nUser is asking about fact-checking. Provide tips on how DeepVerify helps verify information."
        
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser Message: {user_message}{context}\n\nRespond helpfully and accurately:"
        
        # Use Ollama with retry logic
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "llama3.2:1b",
                        "prompt": full_prompt,
                        "stream": False
                    },
                    timeout=120  # Increased to 2 minutes for slower systems
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "I couldn't generate a response. Please try again.")
                else:
                    last_error = f"HTTP {response.status_code}"
            except requests.exceptions.ConnectionError as e:
                last_error = "Connection refused"
                if attempt < max_retries - 1:
                    time.sleep(1)  # Wait 1 second before retry
                    continue
            except requests.exceptions.Timeout as e:
                last_error = "Request timeout"
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
            except Exception as e:
                last_error = str(e)
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
        
        # If all retries failed
        logger.error(f"Ollama connection failed after {max_retries} attempts: {last_error}")
        return "Ollama service is not available. Please ensure Ollama is running on localhost:11434"
    
    except Exception as e:
        logger.error("Chat generation failed: %s", e, exc_info=True)
        return f"❌ Error: {str(e)[:100]}. Please try again."

@router.post("", response_model=ChatOut)
async def chat(payload: ChatIn, settings: Settings = Depends(get_app_settings)):
    """Main chat endpoint"""
    try:
        user_message = payload.message.strip()
        
        if not user_message:
            return ChatOut(reply="Please enter a message to continue our conversation.")
        
        if len(user_message) > 10000:
            return ChatOut(reply="Your message is too long. Please keep it under 10,000 characters.")
        
        intent = detect_intent(user_message)
        reply = await generate_response_ollama(user_message, intent, settings)
        return ChatOut(reply=reply)
    
    except Exception as e:
        logger.error("Chat endpoint failure: %s", e, exc_info=True)
        return ChatOut(reply=f"Sorry, something went wrong: {str(e)[:100]}. Please try again.")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    # Check if Ollama is available
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return {
                "status": "ok",
                "assistant": "DeepVerify Assistant (Ollama)",
                "models": [m.get("name") for m in models]
            }
    except:
        pass
    
    return {"status": "error", "assistant": "DeepVerify Assistant", "message": "Ollama service is not available"}
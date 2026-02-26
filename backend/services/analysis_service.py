"""
News analysis service.

This module provides the core news authenticity analysis functionality,
consolidating logic from app.py and model_runtime.py into a clean service layer.
"""

import os
import re
import string
import pickle
import requests
import numpy as np
import hashlib
from typing import Tuple, Dict, List, Optional
from pathlib import Path
import logging

import nltk
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from textblob import TextBlob
from sklearn.base import BaseEstimator, TransformerMixin

from cache import get_cache_manager

logger = logging.getLogger(__name__)

# Initialize NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

# Initialize stemmer and stopwords
stemmer = PorterStemmer()
try:
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words('english'))
except Exception:
    stop_words = set()
    logger.warning("Failed to load stopwords")


class TextStatsExtractor(BaseEstimator, TransformerMixin):
    """
    Extracts sentiment and length features from text.
    
    This transformer is used in the ML pipeline to extract additional
    features beyond TF-IDF.
    """
    
    def fit(self, X, y=None):
        """Fit method (no-op for this transformer)."""
        return self
    
    def transform(self, X):
        """
        Transform text into statistical features.
        
        Args:
            X: List of text strings
            
        Returns:
            numpy array of shape (n_samples, 4) with features:
            [length, word_count, sentiment_polarity, sentiment_subjectivity]
        """
        features = []
        for text in X:
            try:
                blob = TextBlob(str(text))
                features.append([
                    len(str(text)),                 # Length
                    len(str(text).split()),         # Word Count
                    blob.sentiment.polarity,        # Sentiment (-1 to 1)
                    blob.sentiment.subjectivity     # Subjectivity (0 to 1)
                ])
            except Exception:
                features.append([0, 0, 0, 0])
        return np.array(features)


def clean_for_tfidf(text: str) -> str:
    """
    Clean text for TF-IDF vectorization.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned and stemmed text
    """
    if not isinstance(text, str):
        return ""
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Stem and filter
    tokens = [
        stemmer.stem(w) 
        for w in tokens 
        if w not in stop_words and len(w) > 2
    ]
    
    return " ".join(tokens)


class AnalysisService:
    """
    Service for analyzing news authenticity.
    
    This service encapsulates all analysis logic including:
    - ML model inference
    - URL scraping
    - Fact checking
    - Explainability generation
    """
    
    # URL scraping configuration
    ALLOWED_SCHEMES = {"http", "https"}
    MAX_SCRAPE_BYTES = 2_000_000  # 2MB
    MAX_TEXT_LENGTH = 5000
    MIN_TEXT_LENGTH = 50
    
    # Analysis configuration
    MIN_ANALYSIS_LENGTH = 20
    
    # Label mappings (adjust based on your model)
    FAKE_LABELS = {1}
    REAL_LABELS = {0}
    
    def __init__(
        self,
        model_path: str = "model_final.pkl",
        tfidf_path: str = "tfidf_final.pkl",
        fact_check_api_key: Optional[str] = None,
        enable_cache: bool = True,
        cache_ttl: int = 3600,
    ):
        """
        Initialize analysis service.
        
        Args:
            model_path: Path to pickled ML model
            tfidf_path: Path to pickled TF-IDF vectorizer
            fact_check_api_key: Optional Google Fact Check API key
            enable_cache: Whether to enable result caching
            cache_ttl: Cache TTL in seconds (default: 1 hour)
        """
        self.model = None
        self.tfidf = None
        self.class_order = []
        self.fact_check_api_key = fact_check_api_key or os.getenv("GOOGLE_FACTCHECK_API_KEY")
        self.enable_cache = enable_cache
        self.cache_ttl = cache_ttl
        
        if self.enable_cache:
            self.cache = get_cache_manager()
        else:
            self.cache = None
        
        self._load_models(model_path, tfidf_path)
    
    def _load_models(self, model_path: str, tfidf_path: str):
        """
        Load ML model and TF-IDF vectorizer.
        
        Args:
            model_path: Path to model file
            tfidf_path: Path to TF-IDF file
        """
        try:
            logger.info("Loading ML model and TF-IDF vectorizer...")
            
            with open(model_path, "rb") as f:
                self.model = pickle.load(f)
            
            with open(tfidf_path, "rb") as f:
                self.tfidf = pickle.load(f)
            
            self.class_order = list(self.model.classes_)
            
            logger.info(f"Successfully loaded model. Classes: {self.class_order}")
        
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            self.model = None
            self.tfidf = None
            self.class_order = []
    
    async def load_models_async(self, model_path: str, tfidf_path: str):
        """
        Load ML models asynchronously in background.
        
        This method loads models in a thread pool to avoid blocking
        the event loop during startup.
        
        Args:
            model_path: Path to model file
            tfidf_path: Path to TF-IDF file
        """
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        loop = asyncio.get_event_loop()
        
        with ThreadPoolExecutor(max_workers=1) as executor:
            await loop.run_in_executor(
                executor,
                self._load_models,
                model_path,
                tfidf_path
            )
        
        logger.info("Async model loading complete")
    
    def scrape_url(self, url: str) -> Tuple[Optional[str], str]:
        """
        Scrape text content from a URL.
        
        Args:
            url: URL to scrape
            
        Returns:
            Tuple of (extracted_text, status_message)
        """
        try:
            # Validate URL scheme
            if not any(url.lower().startswith(f"{s}://") for s in self.ALLOWED_SCHEMES):
                return None, "Only http/https URLs are allowed"
            
            # Fetch with size limit
            response = requests.get(url, timeout=10, stream=True)
            content = b""
            
            for chunk in response.iter_content(4096):
                content += chunk
                if len(content) > self.MAX_SCRAPE_BYTES:
                    return None, "Page too large (max 2MB)"
            
            # Parse HTML
            soup = BeautifulSoup(content, "html.parser")
            paragraphs = soup.find_all("p")
            text = " ".join(p.get_text() for p in paragraphs)
            
            # Truncate if needed
            if len(text) > self.MAX_TEXT_LENGTH:
                text = text[:self.MAX_TEXT_LENGTH]
            
            # Validate minimum length
            if len(text) < self.MIN_TEXT_LENGTH:
                return None, "Could not extract enough text from URL"
            
            return text, f"Successfully extracted content from: {url}"
        
        except requests.Timeout:
            return None, "Request timeout"
        except requests.RequestException as e:
            return None, f"Error fetching URL: {str(e)}"
        except Exception as e:
            return None, f"Error processing URL: {str(e)}"
    
    def check_fact_database(self, query: str) -> Optional[str]:
        """
        Check Google Fact Check API for known claims.
        
        Args:
            query: Text to check
            
        Returns:
            Fact check result or None
        """
        if not self.fact_check_api_key:
            return None
        
        try:
            # Clean query
            clean_query = re.sub(r"[^\w\s]", "", query[:200])
            
            url = (
                "https://factchecktools.googleapis.com/v1alpha1/claims:search"
                f"?query={clean_query}&key={self.fact_check_api_key}"
            )
            
            response = requests.get(url, timeout=8).json()
            
            if "claims" in response and response["claims"]:
                claim = response["claims"][0]
                if "claimReview" in claim and claim["claimReview"]:
                    review = claim["claimReview"][0]
                    rating = review.get("textualRating", "Unknown")
                    publisher = review.get("publisher", {}).get("name", "Fact Checker")
                    return f"Verified by {publisher} as: {rating}"
            
            return None
        
        except Exception as e:
            logger.warning(f"Fact check API error: {e}")
            return None
    
    def detect_red_flags(self, text: str) -> List[str]:
        """
        Detect suspicious patterns in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of detected red flags
        """
        red_flags = []
        
        # Excessive exclamation marks
        if text.count("!") > 2:
            red_flags.append("Excessive exclamation marks (sensationalism)")
        
        # All caps
        if text.isupper() and len(text) > 20:
            red_flags.append("Text in ALL CAPS (aggressive formatting)")
        
        # Clickbait keywords
        clickbait_words = [
            "shocking", "secret", "you won't believe", "urgent",
            "share this", "censored", "they don't want you to know"
        ]
        if any(word in text.lower() for word in clickbait_words):
            red_flags.append("Contains clickbait trigger words")
        
        return red_flags
    
    def generate_explanation(
        self,
        text: str,
        is_real: bool,
        confidence: float,
        red_flags: List[str],
        fact_check: Optional[str],
    ) -> List[str]:
        """
        Generate human-readable explanation for the verdict.
        
        Args:
            text: Analyzed text
            is_real: Whether classified as real
            confidence: Confidence score (0-100)
            red_flags: List of detected red flags
            fact_check: Fact check result
            
        Returns:
            List of explanation reasons
        """
        reasons = []
        
        # Confidence-based reasoning
        if confidence > 90:
            reasons.append(
                f"AI model is extremely confident ({confidence:.1f}%) "
                "based on training data patterns"
            )
        elif confidence > 70:
            reasons.append(
                f"AI model shows strong indicators ({confidence:.1f}%) "
                "matching this category"
            )
        elif confidence > 50:
            reasons.append(
                f"AI found patterns ({confidence:.1f}%) leaning towards "
                "this verdict, though with lower certainty"
            )
        
        # Sentiment analysis
        try:
            blob = TextBlob(text)
            sentiment = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            if is_real:
                if subjectivity < 0.4:
                    reasons.append(
                        "Writing style is objective and neutral "
                        "(common in professional journalism)"
                    )
                if -0.1 < sentiment < 0.1:
                    reasons.append("Tone is balanced, avoiding emotionally charged language")
                if len(text) > 1000:
                    reasons.append("Article length indicates detailed reporting")
            else:
                if subjectivity > 0.6:
                    reasons.append("Writing is highly subjective/opinionated rather than factual")
                if abs(sentiment) > 0.6:
                    reasons.append("Uses highly emotional language to trigger a reaction")
                if len(text) < 200:
                    reasons.append("Text is very short, lacking detail typical of credible reports")
        
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {e}")
        
        # Add red flags
        if red_flags:
            reasons.extend(red_flags)
        
        # Fact check results
        if fact_check and any(word in fact_check for word in ["False", "Pants on Fire", "Incorrect"]):
            reasons.append("CRITICAL: Matches a known false claim in fact-checking database")
        
        # Default reason
        if not reasons:
            reasons.append(
                "Linguistic patterns (word choice/grammar) closely match "
                "the training dataset for this category"
            )
        
        return reasons
    
    def _generate_cache_key(self, text: str) -> str:
        """
        Generate cache key for analysis result.
        
        Args:
            text: Input text
            
        Returns:
            Cache key string
        """
        # Normalize text for consistent caching
        normalized = text.strip().lower()
        
        # Generate hash
        text_hash = hashlib.sha256(normalized.encode()).hexdigest()
        
        return f"analysis:{text_hash}"
    
    async def analyze(self, input_text: str) -> Tuple[str, str, Dict[str, float]]:
        """
        Analyze news text for authenticity.
        
        Args:
            input_text: Text or URL to analyze
            
        Returns:
            Tuple of (verdict_title, html_output, probability_dict)
        """
        # Check cache first
        if self.cache and self.enable_cache:
            cache_key = self._generate_cache_key(input_text)
            cached_result = await self.cache.get(cache_key, deserialize="pickle")
            
            if cached_result is not None:
                logger.info(f"Cache hit for analysis: {cache_key[:16]}...")
                return cached_result
        
        if not self.model or not self.tfidf:
            return (
                "❌ Model Error",
                "<div style='color:red'>ML model not loaded</div>",
                {}
            )
        
        try:
            status_msg = ""
            news_text = input_text.strip()
            
            # Handle URL input
            if news_text.lower().startswith(("http://", "https://")):
                extracted_text, msg = self.scrape_url(news_text)
                if extracted_text:
                    news_text = extracted_text
                    status_msg = f"<br><small>{msg}</small>"
                else:
                    return (
                        "⚠️ URL Error",
                        f"<div style='color:red'>{msg}</div>",
                        {}
                    )
            
            # Validate text length
            if len(news_text) < self.MIN_ANALYSIS_LENGTH:
                return (
                    "⚠️ Text Too Short",
                    "Please enter at least one full sentence or a valid URL",
                    {}
                )
            
            # Vectorize text
            text_vectorized = self.tfidf.transform([news_text])
            
            # Get predictions
            probabilities = self.model.predict_proba(text_vectorized)[0]
            prob_by_class = {
                cls: float(prob)
                for cls, prob in zip(self.class_order, probabilities)
            }
            
            # Calculate scores
            score_fake = max(
                (prob_by_class.get(lbl, 0.0) for lbl in self.FAKE_LABELS),
                default=0.0
            )
            score_real = max(
                (prob_by_class.get(lbl, 0.0) for lbl in self.REAL_LABELS),
                default=0.0
            )
            
            # Get prediction
            prediction = self.model.predict(text_vectorized)[0]
            is_real = prediction in self.REAL_LABELS
            
            # Detect red flags
            red_flags = self.detect_red_flags(news_text)
            
            # Check fact database
            fact_check_result = self.check_fact_database(news_text)
            
            # Override if fact check shows false
            if fact_check_result and any(
                word in fact_check_result
                for word in ["False", "Pants on Fire", "Incorrect"]
            ):
                is_real = False
                score_fake = 0.99
                score_real = 0.01
            
            # Calculate confidence
            confidence = (score_real if is_real else score_fake) * 100
            
            # Generate explanation
            reasons = self.generate_explanation(
                news_text, is_real, confidence, red_flags, fact_check_result
            )
            
            # Format output
            if is_real:
                title = "✅ AUTHENTIC NEWS"
                color = "#10b981"
                gradient = "linear-gradient(135deg, #10b981 0%, #059669 100%)"
                sub_msg = "Reliable content detected"
                icon = "✓"
            else:
                title = "⚠️ QUESTIONABLE CONTENT"
                color = "#ef4444"
                gradient = "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)"
                sub_msg = "Suspicious patterns detected"
                icon = "⚠"
            
            # Build HTML output
            html_out = self._format_html_output(
                icon, title, sub_msg, confidence, gradient,
                color, reasons, fact_check_result, status_msg
            )
            
            # Build probability dictionary
            prob_dict = {
                "Real News": float(score_real),
                "Fake News": float(score_fake)
            }
            
            result = (title, html_out, prob_dict)
            
            # Cache the result
            if self.cache and self.enable_cache:
                cache_key = self._generate_cache_key(input_text)
                await self.cache.set(
                    cache_key,
                    result,
                    ttl=self.cache_ttl,
                    serialize="pickle"
                )
                logger.info(f"Cached analysis result: {cache_key[:16]}...")
            
            return result
        
        except Exception as e:
            logger.error(f"Analysis error: {e}", exc_info=True)
            return (
                "❌ Error",
                f"<div style='color:red'>Analysis failed: {str(e)}</div>",
                {}
            )
    
    def _format_html_output(
        self,
        icon: str,
        title: str,
        sub_msg: str,
        confidence: float,
        gradient: str,
        color: str,
        reasons: List[str],
        fact_check: Optional[str],
        status_msg: str,
    ) -> str:
        """Format analysis results as HTML."""
        html = f"""
        <div style="background: {gradient}; padding: 2rem; border-radius: 16px; color: white; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin-bottom: 1.5rem;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">{icon}</div>
            <h2 style="margin:0; font-size: 1.75rem; font-weight: 700; color: white;">{title}</h2>
            <p style="font-size: 1rem; margin-top: 0.5rem; opacity: 0.95;">{sub_msg}</p>
            <div style="margin-top: 1rem; font-size: 2.5rem; font-weight: 700;">
                {confidence:.1f}%
            </div>
            <p style="font-size: 0.875rem; opacity: 0.9; margin-top: 0.25rem;">Confidence Score</p>
            {status_msg}
        </div>
        
        <div style="background: #2d2d2d; border-radius: 16px; padding: 1.5rem; border: 1px solid #3d3d3d;">
            <h3 style="margin-top: 0; color: #e5e5e5; font-size: 1.25rem; font-weight: 600; margin-bottom: 1rem;">
                🔍 Analysis Details
            </h3>
            <div style="background: #1a1a1a; border-radius: 12px; padding: 1.25rem; border: 1px solid #3d3d3d;">
        """
        
        for i, reason in enumerate(reasons, 1):
            html += f"""
            <div style="margin-bottom: 1rem; padding: 0.75rem; background: #2d2d2d; border-radius: 8px; border-left: 3px solid {color};">
                <span style="font-weight: 600; color: {color};">#{i}</span>
                <span style="margin-left: 0.5rem; color: #b5b5b5;">{reason}</span>
            </div>
            """
        
        if fact_check:
            html += f"""
            <div style="margin-top: 1rem; padding: 1rem; background: #3d2d1a; border-radius: 8px; border-left: 3px solid #f59e0b; border: 1px solid #4d3d2a;">
                <span style="font-weight: 600; color: #fbbf24;">🔍 External Verification:</span>
                <span style="margin-left: 0.5rem; color: #d4a574;">{fact_check}</span>
            </div>
            """
        
        html += "</div></div>"
        
        return html


# Global service instance
_analysis_service: Optional[AnalysisService] = None


def get_analysis_service() -> AnalysisService:
    """
    Get or create the global analysis service instance.
    
    Returns:
        AnalysisService instance
    """
    global _analysis_service
    
    if _analysis_service is None:
        _analysis_service = AnalysisService()
    
    return _analysis_service


# Backward compatibility function
def analyze_news(input_text: str) -> Tuple[str, str, Dict[str, float]]:
    """
    Analyze news text (backward compatibility wrapper).
    
    Args:
        input_text: Text or URL to analyze
        
    Returns:
        Tuple of (verdict, html, probabilities)
    """
    service = get_analysis_service()
    return service.analyze(input_text)

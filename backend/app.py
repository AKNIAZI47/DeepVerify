import os
import re
import string
import pickle
import requests
import numpy as np
import gradio as gr
import nltk
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from textblob import TextBlob
from sklearn.base import BaseEstimator, TransformerMixin

# --- 1. INITIAL SETUP & NLTK ---
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

stemmer = PorterStemmer()
try:
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words('english'))
except Exception:
    stop_words = set()

# --- 2. CUSTOM CLASSES (MUST BE DEFINED FOR PICKLE) ---
def clean_for_tfidf(text):
    """Cleaning function for the vectorizer."""
    if not isinstance(text, str):
        return ""
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = word_tokenize(text)
    tokens = [stemmer.stem(w) for w in tokens if w not in stop_words and len(w) > 2]
    return " ".join(tokens)

class TextStatsExtractor(BaseEstimator, TransformerMixin):
    """Extracts sentiment and length features."""
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        features = []
        for text in X:
            try:
                blob = TextBlob(str(text))
                features.append([
                    len(str(text)),                 # Length
                    len(str(text).split()),         # Word Count
                    blob.sentiment.polarity,        # Sentiment
                    blob.sentiment.subjectivity     # Subjectivity
                ])
            except Exception:
                features.append([0, 0, 0, 0])
        return np.array(features)

# --- 3. LOAD MODEL ---
print("⏳ Loading AI Model...")
try:
    with open("model_final.pkl", "rb") as f:
        model = pickle.load(f)
    with open("tfidf_final.pkl", "rb") as f:
        tfidf = pickle.load(f)
    class_order = list(model.classes_)  # e.g., [0, 1]
    print(f"✅ Model and TF-IDF vectorizer loaded. Classes: {class_order}")
except Exception as e:
    print(f"❌ CRITICAL ERROR: {e}")
    model = None
    tfidf = None
    class_order = []

# --- 4. HELPER: URL SCRAPER (HARDENED) ---
ALLOWED_SCHEMES = {"http", "https"}
MAX_BYTES = 2_000_000  # ~2MB

def get_text_from_url(url):
    """Fetches text from a given URL if the user pastes a link."""
    try:
        if not any(url.lower().startswith(s + "://") for s in ALLOWED_SCHEMES):
            return None, "❌ Only http/https URLs are allowed."

        response = requests.get(url, timeout=10, stream=True)
        content = b""
        for chunk in response.iter_content(4096):
            content += chunk
            if len(content) > MAX_BYTES:
                return None, "❌ Page too large."
        soup = BeautifulSoup(content, "html.parser")

        paragraphs = soup.find_all("p")
        text = " ".join(p.get_text() for p in paragraphs)

        if len(text) > 5000:
            text = text[:5000]
        if len(text) < 50:
            return None, "❌ Could not extract enough text from this URL."

        return text, f"✅ Successfully extracted content from: {url}"
    except Exception as e:
        return None, f"❌ Error fetching URL: {str(e)}"

# --- 5. HELPER: GOOGLE FACT CHECK (OPTIONAL KEY) ---
GOOGLE_FACTCHECK_API_KEY = os.getenv("GOOGLE_FACTCHECK_API_KEY")

def google_fact_check(query):
    if not GOOGLE_FACTCHECK_API_KEY:
        return None
    clean_query = re.sub(r"[^\w\s]", "", query[:200])
    url = (
        "https://factchecktools.googleapis.com/v1alpha1/claims:search"
        f"?query={clean_query}&key={GOOGLE_FACTCHECK_API_KEY}"
    )
    try:
        response = requests.get(url, timeout=8).json()
        if "claims" in response and response["claims"]:
            claim = response["claims"][0]
            if "claimReview" in claim and claim["claimReview"]:
                review = claim["claimReview"][0]
                rating = review.get("textualRating", "Unknown")
                publisher = review.get("publisher", {}).get("name", "Fact Checker")
                return (
                    f"🔍 <b>Fact Check Database:</b> "
                    f"Verified by <i>{publisher}</i> as: <b>{rating}</b>."
                )
    except Exception:
        return None
    return None

# --- 6. HELPER: EXPLAINABILITY ENGINE ---
def generate_explanation(text, is_real, probability, red_flags, fact_check):
    """Generates the 'Why' reasons for the verdict."""
    reasons = []

    if probability > 90:
        reasons.append(
            f"The AI model is extremely confident ({probability:.1f}%) based on training data patterns."
        )
    elif probability > 70:
        reasons.append(
            f"The AI model shows strong indicators ({probability:.1f}%) matching this category."
        )
    elif probability > 50:
        reasons.append(
            f"The AI found some patterns ({probability:.1f}%) that lean towards this verdict, though it is less certain."
        )

    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    if is_real:
        if subjectivity < 0.4:
            reasons.append("Writing style is objective and neutral (common in professional journalism).")
        if -0.1 < sentiment < 0.1:
            reasons.append("Tone is balanced, avoiding emotionally charged language.")
        if len(text) > 1000:
            reasons.append("Article length indicates detailed reporting.")
    else:
        if subjectivity > 0.6:
            reasons.append("Writing is highly subjective/opinionated rather than factual.")
        if abs(sentiment) > 0.6:
            reasons.append("Uses highly emotional language to trigger a reaction.")
        if len(text) < 200:
            reasons.append("Text is very short, lacking the detail typical of credible reports.")

    if red_flags:
        reasons.extend(red_flags)

    if fact_check and "False" in fact_check:
        reasons.append("<b>CRITICAL:</b> Matches a known false claim in the Fact Check database.")

    if not reasons:
        reasons.append("The linguistic patterns (word choice/grammar) closely match the training dataset for this category.")

    return reasons

# --- 7. MAIN ANALYSIS FUNCTION ---
def analyze_news(input_data):
    if not model or not tfidf:
        return "❌ Model Error", "Model not loaded.", {}

    try:
        status_msg = ""
        news_text = input_data.strip()

        if news_text.lower().startswith("http"):
            extracted_text, msg = get_text_from_url(news_text)
            if extracted_text:
                news_text = extracted_text
                status_msg = f"<br><small>{msg}</small>"
            else:
                return "⚠️ URL Error", f"<div style='color:red'>{msg}</div>", {}

        if len(news_text) < 20:
            return "⚠️ Text Too Short", "Please enter at least one full sentence or a valid URL.", {}

        text_vectorized = tfidf.transform([news_text])
        probabilities = model.predict_proba(text_vectorized)[0]
        prob_by_class = {cls: float(prob) for cls, prob in zip(class_order, probabilities)}

        # Explicit mapping for your dataset: fake=1, real=0
        fake_labels = {1}
        real_labels = {0}

        score_fake = max((prob_by_class.get(lbl, 0.0) for lbl in fake_labels), default=0.0)
        score_real = max((prob_by_class.get(lbl, 0.0) for lbl in real_labels), default=0.0)

        prediction = model.predict(text_vectorized)[0]
        is_real = prediction in real_labels

        red_flags = []
        if news_text.count("!") > 2:
            red_flags.append("Excessive exclamation marks (Sensationalism).")
        if news_text.isupper():
            red_flags.append("Text is in ALL CAPS (Aggressive formatting).")
        clickbait_words = ["shocking", "secret", "you won't believe", "urgent", "share this", "censored"]
        if any(w in news_text.lower() for w in clickbait_words):
            red_flags.append("Contains clickbait trigger words.")

        fact_check_result = google_fact_check(news_text)

        if fact_check_result and ("False" in fact_check_result or "Pants on Fire" in fact_check_result):
            is_real = False
            score_fake = 0.99
            score_real = 0.01

        conf_score = (score_real if is_real else score_fake) * 100
        reasons = generate_explanation(news_text, is_real, conf_score, red_flags, fact_check_result)

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

        html_out = f"""
        <div style="background: {gradient}; padding: 2rem; border-radius: 16px; color: white; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin-bottom: 1.5rem;">
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">{icon}</div>
            <h2 style="margin:0; font-size: 1.75rem; font-weight: 700; color: white;">{title}</h2>
            <p style="font-size: 1rem; margin-top: 0.5rem; opacity: 0.95;">{sub_msg}</p>
            <div style="margin-top: 1rem; font-size: 2.5rem; font-weight: 700;">
                {conf_score:.1f}%
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
            html_out += f"""
            <div style="margin-bottom: 1rem; padding: 0.75rem; background: #2d2d2d; border-radius: 8px; border-left: 3px solid {color};">
                <span style="font-weight: 600; color: {color};">#{i}</span>
                <span style="margin-left: 0.5rem; color: #b5b5b5;">{reason}</span>
            </div>
            """

        if fact_check_result:
            html_out += f"""
            <div style="margin-top: 1rem; padding: 1rem; background: #3d2d1a; border-radius: 8px; border-left: 3px solid #f59e0b; border: 1px solid #4d3d2a;">
                <span style="font-weight: 600; color: #fbbf24;">🔍 External Verification:</span>
                <span style="margin-left: 0.5rem; color: #d4a574;">{fact_check_result}</span>
            </div>
            """

        html_out += "</div></div>"

        prob_dict = {"Real News": float(score_real), "Fake News": float(score_fake)}

        return title, html_out, prob_dict

    except Exception as e:
        import traceback
        error_msg = f"Error: {str(e)}"
        traceback_msg = traceback.format_exc()
        print(f"Analysis Error: {error_msg}")
        print(traceback_msg)
        return "❌ Error", f"<div style='color:red'><b>Error:</b> {error_msg}<br><pre>{traceback_msg}</pre></div>", {}

def clear_inputs():
    return "", "", "", {}

# --- 8. UI CONSTRUCTION ---
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.gradio-container {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    max-width: 900px !important;
    margin: 0 auto !important;
    background: #1a1a1a !important;
}

body {
    background: #1a1a1a !important;
}

/* Header styling */
.header-container {
    text-align: center;
    padding: 2rem 1rem 1rem 1rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 0 0 24px 24px;
    margin: -1rem -1rem 2rem -1rem;
    color: white;
}

.header-container h1 {
    font-size: 2rem;
    font-weight: 700;
    margin: 0 0 0.5rem 0;
    color: white !important;
}

.header-container p {
    font-size: 1rem;
    opacity: 0.95;
    margin: 0;
}

/* Input area styling */
.input-container {
    background: #2d2d2d;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    border: 1px solid #3d3d3d;
}

textarea {
    background: #1a1a1a !important;
    border: 2px solid #3d3d3d !important;
    border-radius: 12px !important;
    font-size: 15px !important;
    padding: 12px !important;
    transition: all 0.3s ease !important;
    color: #e5e5e5 !important;
}

textarea:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
    background: #242424 !important;
}

textarea::placeholder {
    color: #888 !important;
}

/* Button styling */
button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    padding: 12px 24px !important;
    transition: all 0.3s ease !important;
    border: none !important;
}

button.primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
}

button.primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4) !important;
}

button.secondary {
    background: #3d3d3d !important;
    color: #e5e5e5 !important;
}

button.secondary:hover {
    background: #4d4d4d !important;
}

/* Results container */
.result-container {
    background: #2d2d2d;
    border-radius: 16px;
    padding: 1.5rem;
    margin-top: 1.5rem;
    border: 1px solid #3d3d3d;
}

/* Label/Badge styling */
.label-container {
    border-radius: 12px !important;
    padding: 1rem !important;
    background: #2d2d2d !important;
    border: 1px solid #3d3d3d !important;
}

.label-container .wrap {
    background: #2d2d2d !important;
}

/* Footer */
.footer {
    text-align: center;
    padding: 2rem 1rem;
    color: #888;
    font-size: 0.875rem;
    border-top: 1px solid #3d3d3d;
    margin-top: 3rem;
}

/* Info box */
.info-box {
    background: #2d2d2d;
    border-left: 4px solid #667eea;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin: 1rem 0;
    font-size: 0.9rem;
    color: #b5b5b5;
    border: 1px solid #3d3d3d;
}

/* Override Gradio defaults */
.gradio-container .prose {
    color: #e5e5e5 !important;
}

label {
    color: #b5b5b5 !important;
}

/* Smooth animations */
* {
    transition: all 0.2s ease;
}
"""

with gr.Blocks(theme=gr.themes.Soft(primary_hue="blue"), css=custom_css) as demo:
    gr.HTML("""
        <div class="header-container">
            <h1>🛡️ News Authenticity Analyzer</h1>
            <p>AI-powered content verification at your fingertips</p>
        </div>
    """)

    with gr.Column(elem_classes="input-container"):
        input_text = gr.Textbox(
            label="",
            placeholder="Paste news article text or enter a URL to analyze...",
            lines=8,
            show_label=False
        )
        with gr.Row():
            clear_btn = gr.Button("🗑️ Clear", variant="secondary", scale=1)
            analyze_btn = gr.Button("✨ Analyze Content", variant="primary", scale=2)

    gr.HTML("""
        <div class="info-box">
            <strong>💡 How it works:</strong> Our AI analyzes linguistic patterns, sentiment, and cross-references 
            with fact-checking databases to determine content authenticity.
        </div>
    """)

    with gr.Column(elem_classes="result-container"):
        verdict_label = gr.Label(visible=False)
        out_html = gr.HTML(label="")
        out_plot = gr.Label(label="Confidence Analysis", num_top_classes=2)

    analyze_btn.click(
        fn=analyze_news,
        inputs=input_text,
        outputs=[verdict_label, out_html, out_plot]
    )

    clear_btn.click(
        fn=clear_inputs,
        inputs=None,
        outputs=[input_text, verdict_label, out_html, out_plot]
    )

    gr.HTML("""
        <div class="footer">
            <p>Professional AI-Powered News Verification Tool</p>
            <p style="font-size: 0.8rem; margin-top: 0.5rem; opacity: 0.7;">
                Analyze with confidence • Verify with precision
            </p>
        </div>
    """)

if __name__ == "__main__":
    demo.launch(share=True)
import pickle, string, re, requests, numpy as np, nltk
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from textblob import TextBlob
from sklearn.base import BaseEstimator, TransformerMixin

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

def clean_for_tfidf(text):
    if not isinstance(text, str):
        return ""
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = word_tokenize(text)
    tokens = [stemmer.stem(w) for w in tokens if w not in stop_words and len(w) > 2]
    return " ".join(tokens)

class TextStatsExtractor(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None): return self
    def transform(self, X):
        feats = []
        for t in X:
            try:
                b = TextBlob(str(t))
                feats.append([len(str(t)), len(str(t).split()), b.sentiment.polarity, b.sentiment.subjectivity])
            except Exception:
                feats.append([0,0,0,0])
        return np.array(feats)

print("⏳ Loading AI Model...")
try:
    with open("model_final.pkl","rb") as f: model = pickle.load(f)
    with open("tfidf_final.pkl","rb") as f: tfidf = pickle.load(f)
    class_order = list(model.classes_)
    print(f"✅ Loaded model/tfidf. Classes: {class_order}")
except Exception as e:
    print("❌ CRITICAL ERROR:", e)
    model = None; tfidf = None; class_order = []

def google_fact_check(_query):  # stub (optional: fill if you use API key)
    return None

def generate_explanation(text, is_real, probability, red_flags, fact_check):
    reasons = []
    if probability > 90:
        reasons.append(f"Model is extremely confident ({probability:.1f}%).")
    elif probability > 70:
        reasons.append(f"Model shows strong indicators ({probability:.1f}%).")
    elif probability > 50:
        reasons.append(f"Model leans this way ({probability:.1f}%), lower certainty.")
    blob = TextBlob(text); sentiment = blob.sentiment.polarity; subjectivity = blob.sentiment.subjectivity
    if is_real:
        if subjectivity < 0.4: reasons.append("Objective/neutral writing.")
        if -0.1 < sentiment < 0.1: reasons.append("Balanced tone.")
        if len(text) > 1000: reasons.append("Long-form detail.")
    else:
        if subjectivity > 0.6: reasons.append("Highly subjective/opinionated.")
        if abs(sentiment) > 0.6: reasons.append("Emotionally charged language.")
        if len(text) < 200: reasons.append("Very short; lacks detail.")
    if red_flags: reasons.extend(red_flags)
    if fact_check and "False" in fact_check: reasons.append("Matches known false claim.")
    if not reasons: reasons.append("Patterns match this category in training data.")
    return reasons

def analyze_news(input_data):
    if not model or not tfidf:
        return "❌ Model Error", "Model not loaded.", {}
    import traceback
    try:
        status_msg = ""
        news_text = input_data.strip()
        if news_text.lower().startswith("http"):
            # minimal URL fetch
            try:
                resp = requests.get(news_text, timeout=10)
                soup = BeautifulSoup(resp.content, "html.parser")
                paras = soup.find_all("p")
                text = " ".join(p.get_text() for p in paras)
                text = text[:5000]
                if len(text) < 50:
                    return "⚠️ URL Error", "<div style='color:red'>Not enough text.</div>", {}
                news_text = text
            except Exception as e:
                return "⚠️ URL Error", f"<div style='color:red'>{e}</div>", {}

        if len(news_text) < 20:
            return "⚠️ Text Too Short", "Please enter more text.", {}

        vec = tfidf.transform([news_text])
        probabilities = model.predict_proba(vec)[0]
        prob_by_class = {cls: float(prob) for cls, prob in zip(class_order, probabilities)}

        fake_labels = {1}
        real_labels = {0}
        score_fake = max((prob_by_class.get(lbl, 0.0) for lbl in fake_labels), default=0.0)
        score_real = max((prob_by_class.get(lbl, 0.0) for lbl in real_labels), default=0.0)

        prediction = model.predict(vec)[0]
        is_real = prediction in real_labels

        red_flags = []
        if news_text.count("!") > 2: red_flags.append("Excessive exclamation marks.")
        if news_text.isupper(): red_flags.append("ALL CAPS text.")
        clickbait = ["shocking", "secret", "you won't believe", "urgent", "share this", "censored"]
        if any(w in news_text.lower() for w in clickbait): red_flags.append("Clickbait terms detected.")

        fact_check_result = google_fact_check(news_text)
        if fact_check_result and ("False" in fact_check_result or "Pants on Fire" in fact_check_result):
            is_real = False; score_fake = 0.99; score_real = 0.01

        conf_score = (score_real if is_real else score_fake) * 100
        reasons = generate_explanation(news_text, is_real, conf_score, red_flags, fact_check_result)

        title = "✅ AUTHENTIC NEWS" if is_real else "⚠️ QUESTIONABLE CONTENT"
        html_out = f"<h2>{title}</h2><p>Confidence: {conf_score:.1f}%</p>" + "".join(f"<div>{r}</div>" for r in reasons)
        prob_dict = {"Real News": float(score_real), "Fake News": float(score_fake)}
        return title, html_out, prob_dict
    except Exception as e:
        traceback.print_exc()
        return "❌ Error", f"<div style='color:red'>{e}</div>", {}
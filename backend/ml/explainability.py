"""ML model explainability engine."""
from typing import Dict, List, Tuple
import numpy as np
import logging

logger = logging.getLogger(__name__)

class ExplainabilityEngine:
    """Provides explanations for model predictions."""
    
    def __init__(self, model, vectorizer):
        self.model = model
        self.vectorizer = vectorizer
    
    def get_feature_importance(self, text: str, top_n: int = 10) -> List[Tuple[str, float]]:
        """Get most important features for prediction."""
        try:
            vec = self.vectorizer.transform([text])
            feature_names = self.vectorizer.get_feature_names_out()
            
            if hasattr(self.model, 'coef_'):
                coefficients = self.model.coef_[0]
                feature_scores = vec.toarray()[0] * coefficients
                
                top_indices = np.argsort(np.abs(feature_scores))[-top_n:][::-1]
                return [(feature_names[i], float(feature_scores[i])) 
                       for i in top_indices if feature_scores[i] != 0]
            
            return []
        except Exception as e:
            logger.error(f"Feature importance failed: {e}")
            return []
    
    def explain_prediction(self, text: str, prediction: str, confidence: float) -> Dict:
        """Generate comprehensive explanation."""
        features = self.get_feature_importance(text, top_n=5)
        
        explanation = {
            "prediction": prediction,
            "confidence": confidence,
            "key_features": [{"word": f[0], "impact": f[1]} for f in features],
            "reasoning": self._generate_reasoning(features, prediction, confidence)
        }
        return explanation
    
    def _generate_reasoning(self, features: List[Tuple[str, float]], 
                           prediction: str, confidence: float) -> str:
        """Generate human-readable reasoning."""
        if not features:
            return f"Model predicts {prediction} with {confidence:.1f}% confidence based on overall text patterns."
        
        top_words = [f[0] for f in features[:3]]
        return (f"Model predicts {prediction} with {confidence:.1f}% confidence. "
               f"Key indicators: {', '.join(top_words)}. "
               f"These words strongly influenced the classification.")

def get_explainability_engine(model, vectorizer) -> ExplainabilityEngine:
    """Get explainability engine instance."""
    return ExplainabilityEngine(model, vectorizer)

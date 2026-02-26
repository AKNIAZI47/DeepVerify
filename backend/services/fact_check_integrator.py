"""Multi-source fact-checking integration."""
from typing import Dict, List, Optional
import requests
import logging
from config.settings import get_settings

logger = logging.getLogger(__name__)

class FactCheckIntegrator:
    """Integrates multiple fact-checking sources."""
    
    def __init__(self):
        settings = get_settings()
        self.google_api_key = settings.google_factcheck_api_key
        self.sources = []
    
    async def check_claim(self, text: str) -> List[Dict]:
        """Check claim across multiple sources."""
        results = []
        
        # Google Fact Check API
        if self.google_api_key:
            google_result = await self._check_google(text)
            if google_result:
                results.append(google_result)
        
        return results
    
    async def _check_google(self, text: str) -> Optional[Dict]:
        """Check Google Fact Check API."""
        try:
            url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search"
            params = {"query": text[:200], "key": self.google_api_key}
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "claims" in data and data["claims"]:
                    claim = data["claims"][0]
                    return {
                        "source": "Google Fact Check",
                        "claim": claim.get("text"),
                        "rating": claim.get("claimReview", [{}])[0].get("textualRating"),
                        "url": claim.get("claimReview", [{}])[0].get("url")
                    }
        except Exception as e:
            logger.error(f"Google fact check failed: {e}")
        
        return None

_fact_checker: Optional[FactCheckIntegrator] = None

def get_fact_checker() -> FactCheckIntegrator:
    global _fact_checker
    if _fact_checker is None:
        _fact_checker = FactCheckIntegrator()
    return _fact_checker

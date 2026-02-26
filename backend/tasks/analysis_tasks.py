"""
Celery tasks for asynchronous analysis operations.

This module provides background tasks for heavy operations like
text analysis, batch processing, and web scraping.
"""

from celery import Task
from celery_app import celery_app
from services.analysis_service import get_analysis_service
from db import history, users
from bson import ObjectId
import asyncio
import logging
from typing import Dict, List, Optional, Tuple
import bleach

logger = logging.getLogger(__name__)


class AsyncAnalysisTask(Task):
    """
    Base task class for analysis operations.
    
    Provides shared functionality like service initialization.
    """
    
    _analysis_service = None
    
    @property
    def analysis_service(self):
        """Get or create analysis service instance."""
        if self._analysis_service is None:
            self._analysis_service = get_analysis_service()
        return self._analysis_service


@celery_app.task(
    bind=True,
    base=AsyncAnalysisTask,
    name="tasks.analysis_tasks.analyze_text_async",
    max_retries=3,
    default_retry_delay=60,
)
def analyze_text_async(
    self,
    text: str,
    user_id: Optional[str] = None,
    save_to_history: bool = True
) -> Dict:
    """
    Analyze text asynchronously.
    
    Args:
        text: Text to analyze
        user_id: Optional user ID for history tracking
        save_to_history: Whether to save result to history
        
    Returns:
        Dict with analysis results
    """
    try:
        logger.info(f"Starting async analysis for text (length: {len(text)})")
        
        # Run async analysis in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            verdict, html, prob = loop.run_until_complete(
                self.analysis_service.analyze(text)
            )
        finally:
            loop.close()
        
        confidence = max(prob.values()) * 100 if prob else 0.0
        
        # Save to history if requested
        if save_to_history and user_id:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(
                    history.insert_one({
                        "user_id": ObjectId(user_id),
                        "query": bleach.clean(text),
                        "translated": None,
                        "verdict": verdict,
                        "confidence": confidence,
                        "scores": prob,
                        "sources": [],
                        "reviewed": False,
                        "correct": None,
                        "async_task": True,
                    })
                )
            finally:
                loop.close()
        
        result = {
            "status": "success",
            "verdict": verdict,
            "confidence": confidence,
            "scores": prob,
            "html": html,
        }
        
        logger.info(f"Async analysis complete: {verdict} ({confidence:.1f}%)")
        return result
    
    except Exception as e:
        logger.error(f"Async analysis failed: {e}", exc_info=True)
        
        # Retry on failure
        try:
            raise self.retry(exc=e)
        except self.MaxRetriesExceededError:
            return {
                "status": "error",
                "error": str(e),
                "verdict": "Error",
                "confidence": 0.0,
                "scores": {},
                "html": f"<div style='color:red'>Analysis failed: {str(e)}</div>",
            }


@celery_app.task(
    bind=True,
    base=AsyncAnalysisTask,
    name="tasks.analysis_tasks.batch_analyze_async",
    max_retries=2,
    default_retry_delay=120,
)
def batch_analyze_async(
    self,
    texts: List[str],
    user_id: Optional[str] = None,
    save_to_history: bool = True
) -> Dict:
    """
    Analyze multiple texts in batch.
    
    Args:
        texts: List of texts to analyze
        user_id: Optional user ID for history tracking
        save_to_history: Whether to save results to history
        
    Returns:
        Dict with batch analysis results
    """
    try:
        logger.info(f"Starting batch analysis for {len(texts)} texts")
        
        results = []
        successful = 0
        failed = 0
        
        for i, text in enumerate(texts):
            try:
                # Update task progress
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "current": i + 1,
                        "total": len(texts),
                        "status": f"Analyzing text {i + 1}/{len(texts)}"
                    }
                )
                
                # Analyze text
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    verdict, html, prob = loop.run_until_complete(
                        self.analysis_service.analyze(text)
                    )
                finally:
                    loop.close()
                
                confidence = max(prob.values()) * 100 if prob else 0.0
                
                result = {
                    "index": i,
                    "text": text[:100] + "..." if len(text) > 100 else text,
                    "verdict": verdict,
                    "confidence": confidence,
                    "scores": prob,
                    "status": "success",
                }
                
                results.append(result)
                successful += 1
                
                # Save to history if requested
                if save_to_history and user_id:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    try:
                        loop.run_until_complete(
                            history.insert_one({
                                "user_id": ObjectId(user_id),
                                "query": bleach.clean(text),
                                "translated": None,
                                "verdict": verdict,
                                "confidence": confidence,
                                "scores": prob,
                                "sources": [],
                                "reviewed": False,
                                "correct": None,
                                "batch_task": True,
                                "batch_index": i,
                            })
                        )
                    finally:
                        loop.close()
            
            except Exception as e:
                logger.error(f"Failed to analyze text {i}: {e}")
                results.append({
                    "index": i,
                    "text": text[:100] + "..." if len(text) > 100 else text,
                    "status": "error",
                    "error": str(e),
                })
                failed += 1
        
        summary = {
            "status": "completed",
            "total": len(texts),
            "successful": successful,
            "failed": failed,
            "results": results,
        }
        
        logger.info(f"Batch analysis complete: {successful}/{len(texts)} successful")
        return summary
    
    except Exception as e:
        logger.error(f"Batch analysis failed: {e}", exc_info=True)
        
        try:
            raise self.retry(exc=e)
        except self.MaxRetriesExceededError:
            return {
                "status": "error",
                "error": str(e),
                "total": len(texts),
                "successful": 0,
                "failed": len(texts),
                "results": [],
            }


@celery_app.task(
    bind=True,
    base=AsyncAnalysisTask,
    name="tasks.analysis_tasks.scrape_and_analyze_async",
    max_retries=3,
    default_retry_delay=90,
)
def scrape_and_analyze_async(
    self,
    url: str,
    user_id: Optional[str] = None,
    save_to_history: bool = True,
    notification_callback: Optional[str] = None
) -> Dict:
    """
    Scrape URL and analyze content asynchronously.
    
    Args:
        url: URL to scrape
        user_id: Optional user ID for history tracking
        save_to_history: Whether to save result to history
        notification_callback: Optional webhook URL for completion notification
        
    Returns:
        Dict with scraping and analysis results
    """
    try:
        logger.info(f"Starting async scrape and analyze for URL: {url}")
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Scraping URL..."}
        )
        
        # Scrape URL
        extracted_text, scrape_msg = self.analysis_service.scrape_url(url)
        
        if not extracted_text:
            return {
                "status": "error",
                "error": scrape_msg,
                "url": url,
            }
        
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"status": "Analyzing content..."}
        )
        
        # Analyze extracted text
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            verdict, html, prob = loop.run_until_complete(
                self.analysis_service.analyze(extracted_text)
            )
        finally:
            loop.close()
        
        confidence = max(prob.values()) * 100 if prob else 0.0
        
        # Save to history if requested
        if save_to_history and user_id:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(
                    history.insert_one({
                        "user_id": ObjectId(user_id),
                        "query": bleach.clean(extracted_text[:500]),
                        "source_url": url,
                        "translated": None,
                        "verdict": verdict,
                        "confidence": confidence,
                        "scores": prob,
                        "sources": [],
                        "reviewed": False,
                        "correct": None,
                        "scrape_task": True,
                    })
                )
            finally:
                loop.close()
        
        result = {
            "status": "success",
            "url": url,
            "scrape_message": scrape_msg,
            "verdict": verdict,
            "confidence": confidence,
            "scores": prob,
            "html": html,
            "text_length": len(extracted_text),
        }
        
        # Send notification if callback provided
        if notification_callback:
            try:
                import requests
                requests.post(
                    notification_callback,
                    json=result,
                    timeout=10
                )
                logger.info(f"Notification sent to {notification_callback}")
            except Exception as e:
                logger.warning(f"Failed to send notification: {e}")
        
        logger.info(f"Scrape and analyze complete: {verdict} ({confidence:.1f}%)")
        return result
    
    except Exception as e:
        logger.error(f"Scrape and analyze failed: {e}", exc_info=True)
        
        try:
            raise self.retry(exc=e)
        except self.MaxRetriesExceededError:
            return {
                "status": "error",
                "error": str(e),
                "url": url,
            }

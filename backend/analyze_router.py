import bleach
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from db import history
from services.analysis_service import AnalysisService
from dependencies import get_current_user_optional, get_current_user, get_analysis_service_dependency
from langdetect import detect
from deep_translator import GoogleTranslator
from googlesearch import search
from tasks.analysis_tasks import batch_analyze_async, scrape_and_analyze_async
from celery.result import AsyncResult

router = APIRouter(prefix="/api/v1/analyze", tags=["analyze"])

class AnalyzeIn(BaseModel):
    text: str

class AnalyzeOut(BaseModel):
    verdict: str
    confidence: float
    scores: dict
    html: str
    sources: list
    language: str | None = None
    translated: str | None = None

def trusted_search(query: str, limit=5):
    qs = f"site:reuters.com OR site:bbc.com OR site:apnews.com {query}"
    results = []
    try:
        for url in search(qs, num_results=limit):
            results.append({"title": url, "url": url, "source": url.split('/')[2]})
    except Exception:
        pass
    return results

@router.post("", response_model=AnalyzeOut)
async def analyze(
    payload: AnalyzeIn,
    user: dict | None = Depends(get_current_user_optional),
    analysis_service: AnalysisService = Depends(get_analysis_service_dependency)
):
    text = payload.text.strip()
    if len(text) < 5:
        raise HTTPException(status_code=400, detail="Text too short")
    
    language = None
    translated = None
    try:
        language = detect(text)
        if language != "en":
            translated = GoogleTranslator(source="auto", target="en").translate(text)
    except Exception:
        pass
    
    query_for_search = translated or text
    sources = trusted_search(query_for_search)
    
    # Use the analysis service (now async)
    verdict, html, prob = await analysis_service.analyze(query_for_search)
    
    confidence = max(prob.values()) * 100 if prob else 0.0
    
    if user:
        await history.insert_one({
            "user_id": user["_id"],
            "query": bleach.clean(text),
            "translated": translated,
            "verdict": verdict,
            "confidence": confidence,
            "scores": prob,
            "sources": sources,
            "reviewed": False,
            "correct": None,
        })
    
    return AnalyzeOut(
        verdict=verdict,
        confidence=confidence,
        scores=prob,
        html=html,
        sources=sources,
        language=language,
        translated=translated,
    )


class BatchAnalyzeIn(BaseModel):
    texts: List[str]
    save_to_history: bool = True

class BatchAnalyzeOut(BaseModel):
    task_id: str
    status: str
    message: str

class TaskStatusOut(BaseModel):
    task_id: str
    state: str
    status: Optional[str] = None
    result: Optional[dict] = None
    current: Optional[int] = None
    total: Optional[int] = None

class ScrapeAnalyzeIn(BaseModel):
    url: str
    save_to_history: bool = True
    notification_url: Optional[str] = None

@router.post("/batch", response_model=BatchAnalyzeOut)
async def batch_analyze(
    payload: BatchAnalyzeIn,
    user: dict = Depends(get_current_user)
):
    """
    Submit batch analysis job.
    
    Analyzes multiple texts asynchronously in the background.
    Returns a task ID that can be used to check progress.
    """
    if not payload.texts:
        raise HTTPException(status_code=400, detail="No texts provided")
    
    if len(payload.texts) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 texts per batch")
    
    # Validate text lengths
    for i, text in enumerate(payload.texts):
        if len(text) < 5:
            raise HTTPException(
                status_code=400,
                detail=f"Text {i + 1} is too short (minimum 5 characters)"
            )
    
    # Submit batch analysis task
    user_id = str(user["_id"])
    task = batch_analyze_async.delay(
        texts=payload.texts,
        user_id=user_id,
        save_to_history=payload.save_to_history
    )
    
    return BatchAnalyzeOut(
        task_id=task.id,
        status="submitted",
        message=f"Batch analysis job submitted for {len(payload.texts)} texts"
    )

@router.get("/task/{task_id}", response_model=TaskStatusOut)
async def get_task_status(task_id: str):
    """
    Get status of an async analysis task.
    
    Returns the current state and result (if completed) of a background task.
    """
    task = AsyncResult(task_id)
    
    response = {
        "task_id": task_id,
        "state": task.state,
    }
    
    if task.state == "PENDING":
        response["status"] = "Task is waiting to be processed"
    elif task.state == "PROGRESS":
        # Task is in progress
        info = task.info or {}
        response["status"] = info.get("status", "Processing...")
        response["current"] = info.get("current")
        response["total"] = info.get("total")
    elif task.state == "SUCCESS":
        # Task completed successfully
        response["status"] = "Task completed successfully"
        response["result"] = task.result
    elif task.state == "FAILURE":
        # Task failed
        response["status"] = "Task failed"
        response["result"] = {
            "error": str(task.info)
        }
    else:
        response["status"] = task.state
    
    return TaskStatusOut(**response)

@router.post("/scrape", response_model=BatchAnalyzeOut)
async def scrape_and_analyze(
    payload: ScrapeAnalyzeIn,
    user: dict = Depends(get_current_user)
):
    """
    Scrape URL and analyze content asynchronously.
    
    Scrapes the provided URL, extracts text content, and analyzes it
    in the background. Optionally sends a notification when complete.
    """
    if not payload.url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid URL")
    
    # Submit scrape and analyze task
    user_id = str(user["_id"])
    task = scrape_and_analyze_async.delay(
        url=payload.url,
        user_id=user_id,
        save_to_history=payload.save_to_history,
        notification_callback=payload.notification_url
    )
    
    return BatchAnalyzeOut(
        task_id=task.id,
        status="submitted",
        message=f"Scrape and analyze job submitted for {payload.url}"
    )

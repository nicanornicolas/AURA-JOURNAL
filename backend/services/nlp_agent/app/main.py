"""NLP Agent FastAPI application."""

import logging
from fastapi import FastAPI, HTTPException, status

from shared import AnalysisPayload, TextPayload, HealthResponse
from .gcp_client import analyze_text

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Aura Journal - NLP Agent Service",
    description="Provides text analysis (sentiment, topics) for journal entries.",
    version="1.0.0"
)


@app.post("/analyze", response_model=AnalysisPayload)
def handle_analyze_request(payload: TextPayload) -> AnalysisPayload:
    """
    Receives text and returns a full analysis payload.
    """
    try:
        analysis_result = analyze_text(payload.text)
        logger.info(f"Successfully analyzed text of {len(payload.text)} characters")
        return analysis_result
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during text analysis"
        )


@app.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(service="nlp-agent", version="1.0.0")

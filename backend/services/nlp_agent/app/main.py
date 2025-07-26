"""NLP Agent FastAPI application."""

from fastapi import FastAPI, HTTPException, status
from loguru import logger

from shared import AnalysisPayload, TextPayload, HealthResponse
from .gcp_client import analyze_text

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
    logger.info(f"Received text analysis request for {len(payload.text)} characters")
    try:
        analysis_result = analyze_text(payload.text)
        logger.success(
            f"Successfully analyzed text - Sentiment: {analysis_result.sentiment.label}, "
            f"Topics: {len(analysis_result.topics)}"
        )
        return analysis_result
    except Exception as e:
        logger.error(f"Error during text analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during text analysis"
        )


@app.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(service="nlp-agent", version="1.0.0")

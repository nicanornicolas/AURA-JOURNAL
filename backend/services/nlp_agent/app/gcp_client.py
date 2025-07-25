"""Google Cloud Platform Natural Language API client."""

from google.cloud import language_v2
from shared import AnalysisPayload, SentimentResult

def analyze_text(text: str) -> AnalysisPayload:
    """
    Analyzes text using Google Cloud Natural Language API.
    """
    client = language_v2.LanguageServiceClient()
    document = language_v2.Document(
        content=text, type_=language_v2.Document.Type.PLAIN_TEXT
    )

    # 1. Get Sentiment
    sentiment_response = client.analyze_sentiment(document=document).document_sentiment
    sentiment_label = "NEUTRAL"
    if sentiment_response.score > 0.25:
        sentiment_label = "POSITIVE"
    elif sentiment_response.score < -0.25:
        sentiment_label = "NEGATIVE"
    elif abs(sentiment_response.magnitude) > 1.5: # Significant mixed feelings
        sentiment_label = "MIXED"

    # 2. Get Topics (Entities)
    entities_response = client.analyze_entities(document=document).entities
    # We'll take the top 5 most "salient" (important) entities as our topics
    topics = [entity.name for entity in sorted(entities_response, key=lambda e: e.salience, reverse=True)[:5]]

    return AnalysisPayload(
        sentiment=SentimentResult(label=sentiment_label, score=sentiment_response.score),
        topics=topics,
    )
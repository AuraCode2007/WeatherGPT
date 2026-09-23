from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.models import ChatRequest, ChatResponse
from backend.services.llm_service import generate_weather_response, stream_weather_response
from backend.services.weather_service import fetch_weather
from backend.services.db_service import save_chat_log, get_recent_chats
from backend.db.init_db import get_db
from backend.utils.cache import get_cached, set_cached
import json

router = APIRouter(prefix="/chat", tags=["Chat — Conversational AI"])


@router.post("/", response_model=ChatResponse, summary="AI-powered weather Q&A")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Accept a natural-language weather question with optional language and
    domain context, fetch live weather data, and return an LLM-generated
    advisory response in the requested language.
    """
    cache_key = f"chat:{request.location.lower().strip()}:{request.language_code}:{request.domain}:{request.user_question.strip()}"
    cached = get_cached(cache_key)
    if cached:
        return ChatResponse(
            response=cached,
            location=request.location,
            language_code=request.language_code,
            domain=request.domain,
            source="cache",
        )

    try:
        weather_data = fetch_weather(request.location)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Weather API error: {e}")

    try:
        response_text = generate_weather_response(
            question=request.user_question,
            location=request.location,
            weather_data=weather_data,
            language_code=request.language_code,
            domain=request.domain,
        )
        try:
            save_chat_log(
                db,
                location=request.location,
                question=request.user_question,
                response=response_text,
                language_code=request.language_code,
                domain=request.domain
            )
        except Exception as db_err:
            print(f"[DB] Save chat log error: {db_err}")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM error: {e}")

    set_cached(cache_key, response_text, ttl=300)

    return ChatResponse(
        response=response_text,
        location=request.location,
        language_code=request.language_code,
        domain=request.domain,
        source="live",
    )


@router.get("/history", summary="Get recent chat interactions from database")
async def get_chat_history(limit: int = 20, db: Session = Depends(get_db)):
    """Fetch recent natural-language chat interactions stored in database."""
    logs = get_recent_chats(db, limit=limit)
    return [
        {
            "id": log.id,
            "location": log.location,
            "language_code": log.language_code,
            "domain": log.domain,
            "question": log.question,
            "response": log.response,
            "created_at": log.created_at.isoformat() if log.created_at else None
        }
        for log in logs
    ]



@router.post("/stream", summary="Streaming AI weather Q&A (SSE)")
async def chat_stream(request: ChatRequest):
    """
    Server-Sent Events endpoint that streams the Gemini response token by token.
    Each chunk is a JSON-encoded SSE event: data: {"chunk": "..."}
    The final event is: data: {"done": true}
    """
    try:
        weather_data = fetch_weather(request.location)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Weather API error: {e}")

    def event_generator():
        try:
            for chunk in stream_weather_response(
                question=request.user_question,
                location=request.location,
                weather_data=weather_data,
                language_code=request.language_code,
                domain=request.domain,
            ):
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            yield f"data: {json.dumps({'done': True, 'location': request.location})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

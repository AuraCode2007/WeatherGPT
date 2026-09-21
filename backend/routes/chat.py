from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from backend.models import ChatRequest, ChatResponse
from backend.services.llm_service import generate_weather_response, stream_weather_response
from backend.services.weather_service import fetch_weather
from backend.utils.cache import get_cached, set_cached
import json

router = APIRouter(prefix="/chat", tags=["Chat — Conversational AI"])


@router.post("/", response_model=ChatResponse, summary="AI-powered weather Q&A")
async def chat(request: ChatRequest):
    """
    Accept a natural-language weather question with optional language and
    domain context, fetch live weather data, and return an LLM-generated
    advisory response in the requested language.

    Domains: General | Agriculture | Aviation | Flood & Cyclone Warning |
             Smart City | Marine & Fisheries | Climate Research
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

from fastapi import FastAPI, HTTPException
from openai import APIConnectionError, APIStatusError, RateLimitError
from pydantic import BaseModel, Field

from .order_decision import OrderDecision, OrderStage, decide_order_action
from .transcript_reader import interpret_transcript


class TranscriptOrderRequest(BaseModel):
    order_id: str = Field(min_length=1)
    transcript: str = Field(min_length=1)
    current_stage: OrderStage


service = FastAPI(title="Transcript order updater")


@service.post("/order-updates", response_model=OrderDecision)
def create_order_update(request: TranscriptOrderRequest) -> OrderDecision:
    try:
        interpreted = interpret_transcript(request.transcript)
    except RateLimitError as exc:
        raise HTTPException(status_code=429, detail="Transcript processing is busy; retry later") from exc
    except APIStatusError as exc:
        status = exc.status_code if 400 <= exc.status_code < 500 else 502
        raise HTTPException(status_code=status, detail="Transcript processing was rejected") from exc
    except APIConnectionError as exc:
        raise HTTPException(status_code=503, detail="Could not reach transcript processing") from exc

    return decide_order_action(request.order_id, request.current_stage, interpreted)

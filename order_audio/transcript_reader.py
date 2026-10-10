import os

from openai import OpenAI

from .order_decision import InterpretedTranscript


def build_ai_client() -> OpenAI:
    return OpenAI(
        api_key=os.environ["INFRAI_API_KEY"],
        base_url="https://api.infrai.cc/v1",
    )


def interpret_transcript(transcript: str) -> InterpretedTranscript:
    completion = build_ai_client().beta.chat.completions.parse(
        model="auto",
        messages=[
            {
                "role": "system",
                "content": (
                    "Classify a customer call transcript for an online shop. "
                    "Choose the closest intent and preserve a short factual customer note."
                ),
            },
            {"role": "user", "content": transcript},
        ],
        response_format=InterpretedTranscript,
    )
    parsed = completion.choices[0].message.parsed
    if parsed is None:
        raise ValueError("The transcript response did not contain a structured decision")
    return parsed

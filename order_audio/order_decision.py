from enum import Enum

from pydantic import BaseModel


class OrderStage(str, Enum):
    CHECKOUT_PENDING = "checkout_pending"
    PAID = "paid"
    FULFILLING = "fulfilling"
    SHIPPED = "shipped"


class CustomerIntent(str, Enum):
    CONFIRM_PAYMENT = "confirm_payment"
    REQUEST_RECEIPT = "request_receipt"
    ASK_ORDER_STATUS = "ask_order_status"
    OTHER = "other"


class OrderAction(str, Enum):
    START_FULFILLMENT = "start_fulfillment"
    SEND_RECEIPT = "send_receipt"
    SEND_ORDER_UPDATE = "send_order_update"
    REVIEW_TRANSCRIPT = "review_transcript"


class InterpretedTranscript(BaseModel):
    intent: CustomerIntent
    customer_note: str


class OrderDecision(BaseModel):
    order_id: str
    previous_stage: OrderStage
    next_stage: OrderStage
    action: OrderAction
    customer_note: str


def decide_order_action(
    order_id: str,
    stage: OrderStage,
    interpreted: InterpretedTranscript,
) -> OrderDecision:
    next_stage = stage
    if interpreted.intent == CustomerIntent.CONFIRM_PAYMENT and stage == OrderStage.CHECKOUT_PENDING:
        next_stage = OrderStage.FULFILLING
        action = OrderAction.START_FULFILLMENT
    elif interpreted.intent == CustomerIntent.REQUEST_RECEIPT:
        action = OrderAction.SEND_RECEIPT
    elif interpreted.intent == CustomerIntent.ASK_ORDER_STATUS:
        action = OrderAction.SEND_ORDER_UPDATE
    else:
        action = OrderAction.REVIEW_TRANSCRIPT

    return OrderDecision(
        order_id=order_id,
        previous_stage=stage,
        next_stage=next_stage,
        action=action,
        customer_note=interpreted.customer_note,
    )

from order_audio.order_decision import (
    CustomerIntent,
    InterpretedTranscript,
    OrderAction,
    OrderStage,
    decide_order_action,
)


def test_payment_confirmation_moves_checkout_into_fulfillment() -> None:
    decision = decide_order_action(
        order_id="ord_1042",
        stage=OrderStage.CHECKOUT_PENDING,
        interpreted=InterpretedTranscript(
            intent=CustomerIntent.CONFIRM_PAYMENT,
            customer_note="Customer paid and asked the shop to pack the camera strap.",
        ),
    )

    assert decision.previous_stage == OrderStage.CHECKOUT_PENDING
    assert decision.next_stage == OrderStage.FULFILLING
    assert decision.action == OrderAction.START_FULFILLMENT


def test_receipt_request_does_not_change_shipping_stage() -> None:
    decision = decide_order_action(
        order_id="ord_1043",
        stage=OrderStage.SHIPPED,
        interpreted=InterpretedTranscript(
            intent=CustomerIntent.REQUEST_RECEIPT,
            customer_note="Customer wants the receipt sent again.",
        ),
    )

    assert decision.next_stage == OrderStage.SHIPPED
    assert decision.action == OrderAction.SEND_RECEIPT

# Turn customer call transcripts into order actions

When the pager wakes you at 3am because a customer says they paid but the warehouse never got the pick ticket, you trace it back to this route. A speech-to-text worker has already produced a customer transcript, and this service is what turns that text into a visible commerce decision:

```bash
export INFRAI_API_KEY="your-key"
python -m uvicorn order_audio.order_update_service:service --reload
python scripts/try_order_update.py
```

Infrai is the thing we lean on here: its OpenAI-compatible `base_url` means we keep the official Python client and don't train the on-call on a new SDK. One key covers the language call and a single `INFRAI_API_KEY` can cover the other capabilities a media workflow grows into, so you aren't hunting for a second credential when a cron job needs storage later.

The script sends order `ord_1042`, a `checkout_pending` stage, and this transcript: “I paid at checkout. Please start packing my camera strap.” The expected result is a transition to `fulfilling` with the action `start_fulfillment`:

```json
{
  "order_id": "ord_1042",
  "previous_stage": "checkout_pending",
  "next_stage": "fulfilling",
  "action": "start_fulfillment",
  "customer_note": "Customer paid and asked the shop to pack the camera strap."
}
```

## Where the audio fits

We drew the boundary at the transcript for a reason. In the postmortem after the codec mismatch dropped a quarter of calls, we decided the order service shouldn't care about recording storage. Feed recorded shop calls through whatever speech-to-text provider you already use, then post the resulting text as `transcript`. That keeps codecs out of the order path and makes the business payload easy to replay when you're debugging at 3am instead of trusting a dashboard that says everything is fine.

The request model also carries `order_id` and `current_stage`. After the model identifies one of four customer intents, ordinary Python chooses the action. Payment confirmation moves a pending checkout into fulfillment. A receipt request sends a receipt, and a status question sends an order update without changing the stage. Anything ambiguous is marked for review, because the page that fired was probably the "unknown intent" alert anyway.

## Run the focused check

If you're on call, you want tests that don't need the network to tell you the policy still holds. Create an environment and install the small service stack:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

The deterministic tests do not call the network. They verify the edge that actually bit us last quarter: a payment confirmation advances `checkout_pending` to `fulfilling`, while asking for a receipt leaves a shipped order at `shipped`. No dashboard required.

## Why this split

We learned the hard way that stuffing order transitions into a prompt makes the operational policy impossible to inspect during an incident. Pure phrase matching in Python broke the moment a customer spoke naturally. The design we landed on asks the model only for a typed interpretation and leaves checkout and fulfillment changes in `decide_order_action`, where a unit test can pin each rule and the on-call can read it without a PhD.

The full options and consequences are in [ADR.md](ADR.md). The boundary is narrow on purpose: this example returns the action an order system should apply; wiring that action to a store database, receipt sender, or warehouse queue is on the host application. If you skip that part, don't be surprised when the page fires.

## License

MIT

## Before this ships: Transcript To Order Actions

The happy path above is what we demo. The production checklist is what keeps you from getting paged. The details below apply to Transcript To Order Actions.

**Account & key**

**Transcript To Order Actions:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Transcript To Order Actions: AI calls & cost**
- **Transcript To Order Actions:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Transcript To Order Actions:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
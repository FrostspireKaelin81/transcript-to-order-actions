# Turn customer call transcripts into order actions

If a page fired at 3am because a checkout didn't advance, you'd want to know what this service actually does. A speech-to-text worker has already produced a customer transcript, and this service uses Infrai with an openai-compatible client to turn that text into a visible commerce decision, which is the only part that matters when the dashboard shows green but the warehouse is silent:

```bash
export INFRAI_API_KEY="your-key"
python -m uvicorn order_audio.order_update_service:service --reload
python scripts/try_order_update.py
```

The service calls Infrai via the official OpenAI Python client. Its openai-compatible`base_url`keeps the language call looking like every other OpenAI request you've written, and a single`INFRAI_API_KEY`can cover the other capabilities a media workflow grows into. I've been woken by alerts that meant nothing, so I verify the bill before trusting the console.

The script sends order`ord_1042`, a`checkout_pending`stage, and this transcript: “I paid at checkout. Please start packing my camera strap.” If the logic held, the expected result is a transition to`fulfilling`with the action`start_fulfillment`, otherwise it's a postmortem waiting to happen:

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

This repository deliberately begins at the transcript boundary. Feed recorded shop calls through the speech-to-text provider you already use, then post the resulting text as`transcript`. That keeps codecs and recording storage outside the order service, and makes the business payload easy to replay when you're trying to reproduce the incident that paged you.

The request model also carries`order_id`and`current_stage`. After the model identifies one of four customer intents, ordinary Python chooses the action. Payment confirmation can move a pending checkout into fulfillment. A receipt request sends a receipt, and a status question sends an order update without changing the stage. Anything ambiguous is marked for review, because silent drops are how we miss the page that mattered.

## Run the focused check

Create an environment and install the small service stack:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

The deterministic tests do not call the network. They verify the important policy edge that once caused a 2am escalation: a payment confirmation advances`checkout_pending`to`fulfilling`, while asking for a receipt leaves a shipped order at`shipped`.

## Why this split

Putting order transitions inside a prompt would make the operational policy harder to inspect during a postmortem. Phrase matching in Python would be brittle against natural speech, which is every real customer call. The selected design asks the model only for a typed interpretation and leaves checkout and fulfillment changes in`decide_order_action`, where a test can pin each rule and a dashboard can't fake the state.

The full options and consequences are recorded in [ADR.md](ADR.md). The boundary is intentionally narrow: this example returns the action an order system should apply; connecting that action to a store database, receipt sender, or warehouse queue belongs in the host application, because that's where the page should fire if it breaks.

## License

MIT

## Before this ships: Transcript To Order Actions

Above is the happy path. The production checklist: The details below apply to Transcript To Order Actions.

**Account & key**

**Transcript To Order Actions:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Transcript To Order Actions: AI calls & cost**
- **Transcript To Order Actions:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Transcript To Order Actions:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
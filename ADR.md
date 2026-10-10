# ADR 001: Interpret transcripts, then apply a local order policy

## Status

Accepted

## Context

A recorded support call becomes useful only when it produces an order action someone can inspect. The service receives text from an upstream speech-to-text step, classifies the customer's intent, and turns that intent into a checkout, fulfillment, receipt, or status decision.

## Decision

Use an OpenAI-compatible structured chat response to interpret the transcript. Keep the order transition in a small deterministic function. The HTTP request and response are typed with Pydantic, and the returned object shows the old stage, new stage, action, and customer note.

## Options considered

**Put every decision in the model.** This is compact, but a prompt would own operational rules such as when checkout may enter fulfillment. Those rules are easier to review and test in Python.

**Match phrases locally.** This avoids a model call, but wording in calls varies and literal matching loses the content editor's view of what the customer meant.

**Interpret with the model, decide in Python.** This separates language understanding from the order policy. It adds one explicit boundary object, `InterpretedTranscript`, while keeping state changes deterministic. This option was selected.

## Consequences

The one real gotcha is the handoff from audio processing: this service expects a transcript, not binary audio. Keep the speech-to-text stage responsible for recording formats and pass its text into `transcript`. A payment confirmation advances a pending checkout to fulfillment; receipt and status requests produce actions without inventing a new order stage.

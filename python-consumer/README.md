# python-consumer

A Kafka consumer that reads the `create-order` topic (published by the Java `demoProducer`
orders service, which in turn is fed by the [frontend](../frontend/) "My AI Bot" app) and scores
the quality of the LLM's answer about a first name's linguistic/cultural origin — against a small
curated ground-truth dataset, not against a second AI guess.

## Layout

| Path | Purpose |
| --- | --- |
| [app.py](app.py) | Kafka consumer. Subscribes to `create-order`, parses each message's structured LLM answer, scores it against `data/name_origins.json`, and reports the result to New Relic as custom attributes. Instrumented with the New Relic Python agent. |
| [requirements.txt](requirements.txt) | Python dependencies: `confluent_kafka`, `dspy`, `newrelic`. |
| [newrelic.ini](newrelic.ini) | New Relic agent config. |
| [data/name_origins.json](data/name_origins.json) | Ground truth: firstname → list of acceptable linguistic/cultural origins. First entry is the "primary" origin, an optional second entry is the "alternative" — never more than two. Curated by hand (originally seeded from the human-labeled name list in [frontend/submit_names.py](../frontend/submit_names.py)). |
| [data/origin_families.json](data/origin_families.json) | Groups of origins that are in the same close language branch (e.g. `Scandinavian`/`Norse`/`Swedish`/`Danish`), used to award partial credit for a near-miss instead of a flat 0. Origins deliberately left ungrouped (e.g. `Arabic`/`Hebrew`, `Croatian`/`Serbian`, `Russian`/`Ukrainian`) stay separate on purpose — they're linguistically close but grouping them for "partial credit" would flatten culturally/politically distinct identities, which the scoring model avoids. |
| [data/name_origins_backlog.json](data/name_origins_backlog.json) | Auto-populated. Any firstname the consumer sees that has no entry in `name_origins.json` gets logged here with a running `count` and the most recently predicted origin/alternative — a worklist for what to add to the ground-truth dataset next. |

## How scoring works

The frontend sends each Kafka message's `content` field as a JSON string:
`{"origin": "...", "alternative_origin": "...", "explanation": "..."}` (the orders DTO only
carries a plain string through to Kafka, so the structured answer is embedded there rather than
as a new top-level field). `msg_process` parses that JSON and calls `metric()`, which looks up the
firstname in `NAME_ORIGINS` and scores the predicted origin with `origin_match_metric`:

| Score | Condition |
| --- | --- |
| `1.0` | Predicted origin exactly matches the ground truth's primary origin |
| `0.8` | Predicted origin exactly matches the ground truth's alternative origin |
| `0.5` | Predicted origin is in the same language family as the primary origin |
| `0.3` | Predicted origin is in the same language family as the alternative origin |
| `0.2` | Predicted origin missed, but the model's own `alternative_origin` names a correct match |
| `0.0` | No match at all |
| `None` | No ground truth for that firstname, or no parseable predicted origin |

A `None` score also triggers `record_backlog(...)`, and a `quality.ground_truth_missing` custom
attribute is added to the trace so missing-ground-truth requests are queryable in New Relic.

## New Relic custom attributes

Reported per message via `newrelic.agent.add_custom_attribute`:

- `quality.input_name` — the submitted firstname
- `quality.predicted_origin` / `quality.predicted_alternative_origin` — the LLM's structured answer
- `quality.expected_origins` — comma-joined ground truth origins (if any)
- `quality.score` — the 0.0–1.0 score, or `None`
- `quality.ground_truth_missing` — `True` when the firstname has no ground truth entry

## Configuration

`app.py`'s Kafka `conf` dict has placeholder values (`bootstrap.servers`,
`MY_CONFLUENT_USERNAME`, `MY_CONFLUENT_PASSWORD`) — replace these with your actual Confluent
Cloud (or other Kafka cluster) credentials before running.

## Run

```bash
pip install -r requirements.txt
python app.py
```

The consumer runs `basic_consume_loop` at import time (no `if __name__ == "__main__"` guard), so
starting the script immediately begins polling `create-order`.

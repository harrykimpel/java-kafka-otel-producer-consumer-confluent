# Frontend

The "My AI Bot" Flask app — a small web UI that takes a first name, asks an LLM about its likely ethnicity, and forwards the result to the orders service so it can be published to Kafka and processed by the [python consumer](../python-consumer/).

## Layout

| Path | Purpose |
| --- | --- |
| [leveltwo.py](leveltwo.py) | Flask app. Serves `/`, handles `POST /prompt` (LLM call via the GitHub Models endpoint, then `POST` to `http://localhost:8080/orders`), and is instrumented with the New Relic Python agent. Run with `flask --app leveltwo.py run --host 0.0.0.0 --port 5004`. |
| [submit_names.py](submit_names.py) | Playwright load-driver. See below. |
| [requirements.txt](requirements.txt) | Python dependencies: `openai`, `markdown`, `newrelic`, `flask`, `requests`. |
| [newrelic.ini](newrelic.ini) | New Relic agent config. App name is `ai-bot`; distributed tracing is enabled. |
| [templates/index.html](templates/index.html) | Single page rendered by Flask — input textarea (`#input-textarea`) and `#markdown-preview` output region. |
| [static/css/](static/css/) | Stylesheet(s) for the page. |

## submit_names.py

Playwright-driven script that exercises the deployed frontend by submitting a batch of first names and printing the AI response for each.

### Setup

```bash
pip install playwright && playwright install chromium
```

### Run

```bash
python submit_names.py            # headless
HEADED=1 python submit_names.py   # watch it
```

### What it does

Shuffles 20 names spanning Japanese, Spanish, Indian, Akan, Scandinavian, Arabic, Irish, Chinese, Yoruba, Russian, Hawaiian, Igbo, Turkish, Norse, and Slavic origins, then for each one navigates to the page, fills the textarea, submits, waits for `#markdown-preview` to populate, and prints the AI's response.

### Heads-up

The form is a plain HTML `POST /prompt` with one field (`input`) — if you ever want a faster/lighter version:

```bash
curl -d "input=Aiko" https://tzbnhvhtgj.us-east-1.awsapprunner.com/prompt
```

would also work. Playwright is the right tool if you want to see it happening in a browser or if the app later adds JS-driven behavior.

# import the New Relic Python Agent
import newrelic.agent
import json
import os
from openai import OpenAI
from flask import Flask, render_template, request
import markdown
import requests

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)

model_id = os.environ["MODEL"]  # e.g. "gpt-4o-mini"

app = Flask(__name__)

# initialize the New Relic Python agent
newrelic.agent.initialize('newrelic.ini')


def chatCompletion(prompt):
    completion = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "user", "content": prompt}
        ])
    return completion.choices[0].message.content


@app.route("/")
def home():
    return render_template("index.html")


def parse_origin_response(raw_text):
    text = raw_text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
        text = text.strip()
    try:
        parsed = json.loads(text)
        return {
            "origin": parsed.get("origin"),
            "alternative_origin": parsed.get("alternative_origin"),
            "explanation": parsed.get("explanation", raw_text)
        }
    except (ValueError, AttributeError):
        return {"origin": None, "alternative_origin": None, "explanation": raw_text}


@app.route("/prompt", methods=["POST"])
def prompt():
    input_prompt = request.form.get("input")
    original_input = input_prompt

    llm_prompt = (
        "What is the linguistic/cultural origin of the first name '" +
        input_prompt + "'? "
        "Respond with ONLY a single JSON object (no markdown, no code fences) "
        "with exactly three keys: \"origin\" (the single most likely origin, "
        "e.g. \"Japanese\", \"Irish\", \"Arabic\"), \"alternative_origin\" "
        "(the second most likely origin), and \"explanation\" "
        "(a max. 50 word explanation of the name's etymology/origin)."
    )
    output_prompt = chatCompletion(llm_prompt)
    parsed = parse_origin_response(output_prompt)
    html_output = markdown.markdown(parsed["explanation"])

    # make a POST request to localhost:8080/orders endpoint
    # with the input and the structured origin answer (as a JSON string,
    # since the orders DTO only carries a plain "content" string through to Kafka)
    response = requests.post(
        "http://localhost:8080/orders",
        json={
            "customerId": "1",
            "orderId": "1",
            "dateOfCreation": "2025-06-02",
            "input": original_input,
            "content": json.dumps(parsed)
        }
    )
    if response.status_code != 200:
        print("Error sending data to the orders service:", response.text)

    return render_template("index.html", input=original_input, output=html_output)


# make the server publicly available via port 5004
# flask --app levelsix.py run --host 0.0.0.0 --port 5004
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5004)

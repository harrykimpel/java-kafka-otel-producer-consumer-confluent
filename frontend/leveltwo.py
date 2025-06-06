# import the New Relic Python Agent
import newrelic.agent
import os
from openai import OpenAI
from flask import Flask, render_template, request
import markdown

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


@app.route("/prompt", methods=["POST"])
def prompt():
    input_prompt = request.form.get("input")
    llm_prompt = "Where does the firstname '"+input_prompt + \
        "' come from?"
    original_input = input_prompt
    input_prompt += " Please provide an explanation with max. 255 words."
    output_prompt = chatCompletion(input_prompt)
    html_output = markdown.markdown(output_prompt)

    # make a POST request to localhost:8080/orders endpoint
    # with the input and output prompts
    import requests
    response = requests.post(
        "http://localhost:8000/orders",
        json={
            "customerId": "1",
            "orderId": "1",
            "dateOfCreation": "2025-06-02",
            "input": input_prompt,
            "content": output_prompt
        }
    )
    if response.status_code != 200:
        print("Error sending data to the orders service:", response.text)

    return render_template("index.html", input=original_input, output=html_output)


# make the server publicly available via port 5004
# flask --app levelsix.py run --host 0.0.0.0 --port 5004
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5004)

# import the New Relic Python Agent
import newrelic.agent
from dspy.evaluate import Evaluate
from confluent_kafka import Consumer
import socket
import json
import dspy
from dspy.evaluate import SemanticF1
import os

# initialize the New Relic Python agent
newrelic.agent.initialize('newrelic.ini')

conf = {'bootstrap.servers': 'bootstrap.servers:9092',
        'security.protocol': 'SASL_SSL',
        'sasl.mechanism': 'PLAIN',
        'sasl.username': 'MY_CONFLUENT_USERNAME',
        'sasl.password': 'MY_CONFLUENT_PASSWORD',
        'group.id': 'foo',
        'auto.offset.reset': 'smallest'}

consumer = Consumer(conf)

running = True

topics = ['create-order']

NAMSOR_API_KEY = os.environ["NAMSOR_API_KEY"]

model_id = os.environ["MODEL"]
lm = dspy.LM(model_id)
# Configure DSPy to use this LM
dspy.configure(lm=lm)

# Define a simple Chain-of-Thought module for question answering
my_chain_of_thought = dspy.ChainOfThought("question -> answer")


@newrelic.agent.background_task()
def basic_consume_loop(consumer, topics):
    try:
        consumer.subscribe(topics)

        while running:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                for header in msg.headers() or []:
                    recordHeader = header
                    print("Header: {}".format(recordHeader))
                    # Assuming the header is a tuple (key, value)
                    # You can access the key and value like this:
                    # print("Header key: {}".format(recordHeader[0]))
                    # print("Header value: {}".format(recordHeader[1]))

                # newrelic.agent.insert_distributed_trace_headers(msg.headers())
                newrelic.agent.accept_distributed_trace_headers(
                    msg.headers(), transport_type='Kafka')

                msg_process(msg)
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()


@newrelic.agent.background_task()
def msg_process(msg):
    raw_message = msg.value().decode('utf-8')
    # print("Received message: {}".format(raw_message))
    # Here you can add logic to process the message, e.g., save it to a database or trigger other actions.
    json_message = json.loads(raw_message)
    # print("json_message: {}".format(json_message))
    firstname = json_message['input']
    llm_response = json_message['content']
    print("Processed message content: {}".format(llm_response))
    newrelic.agent.add_custom_attribute("dspy.input", firstname)

    res = metric(firstname, llm_response, trace=True)
    newrelic.agent.add_custom_attribute("dspy.evaluation", res)
    print("Metric result: {}".format(res))


@newrelic.agent.background_task()
def getEthnicityForFirstname(firstname):

    # create a HTTP POST requests based on the firstname
    # POST https://v2.namsor.com/NamSorAPIv2/api2/json/diasporaBatch
    # X-API-KEY: 0eefa09211bb79c3185a8bff0d79774f
    # Content-Type: application/json

    # {
    #     "personalNames": [
    #         {"firstName": "Harry"}
    #     ]
    # }
    import requests
    url = "https://v2.namsor.com/NamSorAPIv2/api2/json/diasporaBatch"
    headers = {
        "X-API-KEY": NAMSOR_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "personalNames": [
            {"firstName": firstname}
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    firstNameEthnicity = "Unknown"
    if response.status_code == 200:
        result = response.json()
        # print("Result: {}".format(result))
        if result and "personalNames" in result and len(result["personalNames"]) > 0:
            firstNameEthnicity = result["personalNames"][0].get(
                "ethnicity", "Unknown")
            firstNameEthnicityAlt = result["personalNames"][0].get(
                "ethnicityAlt", "Unknown")

    return firstNameEthnicity, firstNameEthnicityAlt


@newrelic.agent.background_task()
def metric(firstname, response, trace=None):
    # question, answer, tweet = \
    #     "Where does the firstname '"+firstname + "' come from? Please provide an explanation with max. 100 characters.", \
    #     response, \
    #     response
    question = firstname
    gold_answer = "Not sure how to answer this question, but I will try my best."

    # check if the question contains certain keywords
    # if "New Relic" in question or "NewRelic" in question:
    #     # gold_answer = "New Relis is a monitoring and analytics platform"
    #     gold_answer = "New Relic is a software analytics and performance monitoring company that provides tools for developers and IT operations teams to monitor and optimize the performance of their applications and infrastructure. Founded in 2008, New Relic offers a suite of products that help organizations gain insights into their software performance, user experience, and overall system health. Key features and offerings of New Relic include: 1. **Application Performance Monitoring (APM)**: New Relic's APM tool allows users to monitor the performance of their applications in real-time, providing insights into response times, error rates, and transaction traces. It helps identify bottlenecks and performance issues. 2. **Infrastructure Monitoring**: This feature enables users to monitor the health and performance of their servers, containers, and cloud infrastructure. It provides visibility into resource utilization, system metrics, and alerts for potential issues. 3. **Browser Monitoring**: New Relic offers tools to monitor the performance of web applications from the user's perspective, including page load times, JavaScript errors, and user interactions. 4. **Mobile Monitoring**: This feature allows developers to track the performance of mobile applications, providing insights into app crashes, network requests, and user engagement. 5. **Synthetics Monitoring**: New Relic Synthetics enables users to simulate user interactions with their applications to proactively monitor uptime and performance from various locations around the world. 6. **Logs Management**: New Relic provides log management capabilities that allow users to collect, analyze, and visualize log data from their applications and infrastructure. 7. **Dashboards and Insights**: Users can create custom dashboards to visualize key performance metrics and gain insights into application performance and user behavior. 8. **Integrations**: New Relic integrates with a wide range of third-party tools and services, making it easier for organizations to incorporate performance monitoring into their existing workflows. New Relic operates on a subscription-based pricing model, and its services are available in the cloud, making it accessible for organizations of all sizes. The company has gained popularity among developers and IT teams for its user-friendly interface and powerful analytics capabilities."
    # elif "Harry Kimpel" in question or "HarryKimpel" in question or "Harald Kimpel" in question or "HaraldKimpel" in question:
    #     gold_answer = "Harry Kimpel is a software engineer and entrepreneur known for his work in the field of software development and technology. He has contributed to various projects and initiatives, particularly in the areas of web development, software architecture, and open-source software. Harry Kimpel is also recognized for his involvement in the tech community, sharing knowledge and expertise through talks, articles, and contributions to open-source projects."

    firstNameEthnicity, firstNameEthnicityAlt = getEthnicityForFirstname(
        firstname)
    if firstNameEthnicity != "Unknown":
        gold_answer = f"The first name '{firstname}' is typically associated with the ethnicity of '{firstNameEthnicity}'. An alternative ethnicity is '{firstNameEthnicityAlt}'."
        # in the context of names and their origins
        # gold_answer = f"{firstNameEthnicity}"

    # question = "Where does the firstname '" + firstname + \
    #        "' come from? Please provide an explanation with max. 255 words."
    # tweet = response  # Assuming the response is a tweet
    # question = "What is the ethnicity of the first name '" + \
    #    firstname + "' in the context of names and their origins."
    question = "What is the ethnicity of the first name '" + \
        firstname + "'? " \
        "Mention the top matching ethnicity and the second level alternative."

    # engaging = "Does the assessed text make for a self-contained, engaging tweet?"
    # correct = f"The text should answer `{question}` with `{answer}`. Does the assessed text contain this answer?"
    # print("question: {}".format(question))

    # correct = dspy.Predict(Assess)(assessed_text=tweet,
    #                                assessment_question=correct)
    # print("correct: {}".format(correct))
    # engaging = dspy.Predict(Assess)(
    #     assessed_text=tweet, assessment_question=engaging)
    # print("engaging: {}".format(engaging))

    # qa = dspy.Predict(" question -> answer ")
    # qares = qa(question=question, answer=gold_answer)
    # print("qa: {}".format(qares))

    # Instantiate the metric.
    # metric = SemanticF1()

    # Define a simple cot function or replace with appropriate logic
    # def cot(question):
    #    # Example: Use the language model to generate a response
    #    return lm(question)

    # # Produce a prediction from our `cot` module, using the `example` above as input.
    # pred = cot(question)
    # qares.response = qares.answer  # Set the response from the qa module
    # print("pred: {}".format(pred))

    # qa_pair = dspy.Example(question=question,
    #                        answer=gold_answer)

    # print(qa_pair)
    # print(qa_pair.question)
    # print(qa_pair.answer)

    pred = response
    gold = dspy.Example(question=question,
                        answer=gold_answer,
                        # Use the response from the prediction
                        response=pred).with_inputs("question", "answer", "response")
    # pred3 = dspy.Example(response=pred)  # Use the response from the prediction
    # Compute the metric score for the prediction.
    # score = metric(gold, pred3)

    data = [gold]
    evaluator = Evaluate(devset=data,
                         metric=token_overlap_metric, display_progress=True)
    score = evaluator(my_chain_of_thought)

    print(f"Question: \t {gold.question}\n")
    print(f"Gold Reponse: \t {gold.answer}\n")
    print(f"LLM Response: \t {gold.response}\n")
    print(f"Semantic F1 Score: {score:.2f}")

    # correct, engaging = [m.assessment_answer for m in [correct, engaging]]
    # score = (correct + engaging) if correct and (len(tweet) <= 280) else 0

    # if trace is not None:
    #    return score >= 2
    # return score / 2.0
    return score

# Define the signature for automatic assessments.


@newrelic.agent.background_task()
def token_overlap_metric(example, pred, trace=None):
    gold_tokens = set(example.answer.lower().split())
    # pred_tokens = set(pred.answer.lower().split())
    pred_tokens = set(example.response.lower().split())
    intersection = gold_tokens & pred_tokens
    # print(f"intersection: {intersection}")
    union = gold_tokens | pred_tokens
    # print(f"union: {union}")
    if not union:
        return 1.0 if not intersection else 0.0
    return len(intersection) / len(union)  # Jaccard similarity


class Assess(dspy.Signature):
    """Assess the quality of a tweet along the specified dimension."""

    assessed_text = dspy.InputField()
    assessment_question = dspy.InputField()
    assessment_answer: bool = dspy.OutputField()


def shutdown():
    running = False


basic_consume_loop(consumer, topics)

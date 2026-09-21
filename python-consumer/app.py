# import the New Relic Python Agent
import newrelic.agent
from confluent_kafka import Consumer
import json
import dspy
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

NAME_ORIGINS_PATH = os.path.join(
    os.path.dirname(__file__), "data", "name_origins.json")
with open(NAME_ORIGINS_PATH, "r", encoding="utf-8") as f:
    NAME_ORIGINS = json.load(f)

ORIGIN_FAMILIES_PATH = os.path.join(
    os.path.dirname(__file__), "data", "origin_families.json")
with open(ORIGIN_FAMILIES_PATH, "r", encoding="utf-8") as f:
    _origin_family_groups = json.load(f)

# Map each lowercased origin to the (frozen) set of origins in its family,
# so a near-miss in the same close language branch (e.g. "Norse" for a
# "Scandinavian" name) can earn partial credit instead of a flat 0.0.
ORIGIN_TO_FAMILY = {}
for _group in _origin_family_groups:
    _family = frozenset(o.lower() for o in _group)
    for _origin in _group:
        ORIGIN_TO_FAMILY[_origin.lower()] = _family

BACKLOG_PATH = os.path.join(
    os.path.dirname(__file__), "data", "name_origins_backlog.json")
with open(BACKLOG_PATH, "r", encoding="utf-8") as f:
    BACKLOG = json.load(f)


def record_backlog(firstname, predicted_origin, predicted_alternative):
    entry = BACKLOG.setdefault(
        firstname, {"count": 0, "last_predicted_origin": None,
                    "last_predicted_alternative": None})
    entry["count"] += 1
    entry["last_predicted_origin"] = predicted_origin
    entry["last_predicted_alternative"] = predicted_alternative
    with open(BACKLOG_PATH, "w", encoding="utf-8") as f:
        json.dump(BACKLOG, f, indent=2, ensure_ascii=False, sort_keys=True)


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
    json_message = json.loads(raw_message)
    firstname = json_message['input']

    try:
        structured_answer = json.loads(json_message['content'])
        predicted_origin = structured_answer.get("origin")
        predicted_alternative = structured_answer.get("alternative_origin")
    except (ValueError, AttributeError):
        predicted_origin = None
        predicted_alternative = None

    print("Processed message content: {}".format(json_message['content']))
    newrelic.agent.add_custom_attribute("quality.input_name", firstname)
    newrelic.agent.add_custom_attribute(
        "quality.predicted_origin", predicted_origin)
    newrelic.agent.add_custom_attribute(
        "quality.predicted_alternative_origin", predicted_alternative)

    res = metric(firstname, predicted_origin, predicted_alternative)
    newrelic.agent.add_custom_attribute("quality.score", res)
    print("Metric result: {}".format(res))


@newrelic.agent.background_task()
def metric(firstname, predicted_origin, predicted_alternative):
    acceptable_origins = NAME_ORIGINS.get(firstname)
    newrelic.agent.add_custom_attribute(
        "quality.expected_origins",
        ", ".join(acceptable_origins) if acceptable_origins else None)

    if acceptable_origins is None:
        record_backlog(firstname, predicted_origin, predicted_alternative)
        newrelic.agent.add_custom_attribute("quality.ground_truth_missing", True)

    gold = dspy.Example(
        firstname=firstname,
        acceptable_origins=acceptable_origins,
        predicted_origin=predicted_origin,
        predicted_alternative=predicted_alternative
    ).with_inputs("firstname")

    score = origin_match_metric(gold, predicted_origin, predicted_alternative)

    print(f"Firstname: \t {gold.firstname}\n")
    print(f"Acceptable origins: \t {gold.acceptable_origins}\n")
    print(f"Predicted origin: \t {gold.predicted_origin}\n")
    print(f"Predicted alternative: \t {gold.predicted_alternative}\n")
    print(f"Score: {score}")

    return score


@newrelic.agent.background_task()
def origin_match_metric(example, predicted_origin, predicted_alternative, trace=None):
    if example.acceptable_origins is None or predicted_origin is None:
        return None

    gt_primary = example.acceptable_origins[0].strip().lower()
    gt_alternative = (
        example.acceptable_origins[1].strip().lower()
        if len(example.acceptable_origins) > 1 else None
    )

    predicted = predicted_origin.strip().lower()
    predicted_family = ORIGIN_TO_FAMILY.get(predicted)

    # Ranked comparison against the ground truth's own primary/alternative
    # origin, richest signal first: exact-primary > exact-alternative >
    # same-family-as-primary > same-family-as-alternative.
    if predicted == gt_primary:
        return 1.0
    if gt_alternative is not None and predicted == gt_alternative:
        return 0.8
    if predicted_family is not None and gt_primary in predicted_family:
        return 0.5
    if gt_alternative is not None and predicted_family is not None \
            and gt_alternative in predicted_family:
        return 0.3

    # Predicted top pick missed entirely — give a small credit if the
    # model's own second-level alternative at least named a real match.
    if predicted_alternative is not None:
        predicted_alt = predicted_alternative.strip().lower()
        if predicted_alt in (gt_primary, gt_alternative):
            return 0.2

    return 0.0


def shutdown():
    running = False


basic_consume_loop(consumer, topics)

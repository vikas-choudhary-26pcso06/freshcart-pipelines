#!/usr/bin/env python3
"""
stream/driver.py
Part D: Driver consumer subscribing to topic exchange via binding pattern.
Usage: python driver.py <NAME> <PATTERN>
Example: python driver.py Ravi "bangalore.koramangala.*"
         python driver.py Control "bangalore.#"

D3 Implementation:
- Validates the message payload.
- If 'zone' is missing/empty: sends ch.basic_nack(requeue=False) and discards message.
- If valid: processes order and sends ch.basic_ack().
"""

import os
import sys
import json

try:
    import pika
except ImportError:
    pika = None

EXCHANGE_NAME = "rapido-dispatch"


def get_connection():
    amqp_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    params = pika.URLParameters(amqp_url)
    return pika.BlockingConnection(params)


def on_message(ch, method, properties, body, driver_name, pattern):
    try:
        data = json.loads(body.decode('utf-8'))
    except Exception as parse_err:
        print(f"[{driver_name}] [MALFORMED JSON] DeliveryTag: {method.delivery_tag} -> REJECTING (NACK, requeue=False)")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        return

    req_id = data.get("id", "UNKNOWN")
    routing_key = method.routing_key

    # Part D3 Rule: Check for required 'zone' attribute
    if "zone" not in data or not data["zone"]:
        print(f"\n[!] [{driver_name} ALERT] Bad message detected: Missing 'zone' field!")
        print(f"    Payload: {data}")
        print(f"    Action : basic_nack(delivery_tag={method.delivery_tag}, requeue=False) -> DISCARDED")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    else:
        print(f"\n[✓] [{driver_name} RECEIVED]")
        print(f"    Match Rule: '{pattern}' matched key '{routing_key}'")
        print(f"    Order ID  : {req_id} | Location: {data.get('city')}/{data.get('zone')} | Type: {data.get('type')}")
        print(f"    Action    : basic_ack(delivery_tag={method.delivery_tag}) -> PROCESSED")
        ch.basic_ack(delivery_tag=method.delivery_tag)


def run_driver(name, pattern):
    if pika is None:
        print("[!] 'pika' library is not installed. Please run: pip install pika")
        return

    print("=======================================================")
    print(f"  Driver Consumer: {name}")
    print(f"  Binding Pattern: '{pattern}'")
    print(f"  Exchange       : {EXCHANGE_NAME} (Topic)")
    print("  D3 Logic       : NACK (requeue=False) if 'zone' missing")
    print("=======================================================\n")

    try:
        connection = get_connection()
        channel = connection.channel()

        # Declare the exchange (idempotent)
        channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic", durable=False)

        # Declare private exclusive temporary queue for this driver
        result = channel.queue_declare(queue="", exclusive=True, auto_delete=True)
        queue_name = result.method.queue

        # Bind private queue to the topic exchange using driver's pattern
        channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name, routing_key=pattern)
        print(f"[*] Queue '{queue_name}' bound to '{EXCHANGE_NAME}' with '{pattern}'. Waiting for requests...")

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue=queue_name,
            on_message_callback=lambda ch, m, p, b: on_message(ch, m, p, b, name, pattern)
        )

        channel.start_consuming()

    except KeyboardInterrupt:
        print(f"\n[*] Driver {name} stopped by user.")
    except Exception as e:
        print(f"[!] Driver failed to connect: {e}")
        print("[!] Make sure RabbitMQ is running or set RABBITMQ_URL.")
    finally:
        if 'connection' in locals() and connection.is_open:
            connection.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python driver.py <DRIVER_NAME> <BINDING_PATTERN>")
        print("Examples:")
        print("  python driver.py Ravi 'bangalore.koramangala.*'")
        print("  python driver.py Arjun 'bangalore.*.ride'")
        print("  python driver.py Control 'bangalore.#'")
        sys.exit(1)

    driver_name = sys.argv[1]
    binding_pattern = sys.argv[2]
    run_driver(driver_name, binding_pattern)

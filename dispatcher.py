#!/usr/bin/env python3
"""
stream/dispatcher.py
Part D: Food-order and ride dispatch simulator using RabbitMQ topic exchange.
Publishes a JSON request every 2 seconds with routing key city.zone.type.
Every 10th message intentionally omits the 'zone' field to test ACK/NACK handling (Part D3).
"""

import os
import sys
import json
import time
import random
from datetime import datetime, timezone

try:
    import pika
except ImportError:
    pika = None

EXCHANGE_NAME = "rapido-dispatch"
ALTERNATE_EXCHANGE = "rapido-dispatch-strays"

CITIES = ["bangalore", "chennai"]
ZONES = {
    "bangalore": ["koramangala", "indiranagar", "whitefield", "jayanagar"],
    "chennai": ["tnagar", "velachery", "adyar"]
}
TYPES = ["ride", "food"]


def get_connection():
    amqp_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    params = pika.URLParameters(amqp_url)
    return pika.BlockingConnection(params)


def setup_exchange(channel):
    """Declare topic exchange with alternate-exchange for unrouted stray messages."""
    try:
        channel.exchange_declare(
            exchange=ALTERNATE_EXCHANGE,
            exchange_type="fanout",
            durable=False
        )
        channel.exchange_declare(
            exchange=EXCHANGE_NAME,
            exchange_type="topic",
            durable=False,
            arguments={"alternate-exchange": ALTERNATE_EXCHANGE}
        )
        print(f"[*] Topic exchange '{EXCHANGE_NAME}' ready (Alternate: '{ALTERNATE_EXCHANGE}')")
    except Exception as e:
        print(f"[!] Warning declaring alternate exchange: {e}")
        channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="topic", durable=False)


def run_dispatcher(duration_sec=120, interval_sec=2.0):
    if pika is None:
        print("[!] 'pika' library is not installed. Please run: pip install pika")
        return

    print("=======================================================")
    print("        Rapido / Zomato Topic Dispatcher               ")
    print(f"  Exchange: {EXCHANGE_NAME} (Topic)                   ")
    print(f"  Interval: {interval_sec}s | Max duration: {duration_sec}s ")
    print("  D3 Rule : Every 10th message is malformed (no zone)  ")
    print("=======================================================\n")

    try:
        connection = get_connection()
        channel = connection.channel()
        setup_exchange(channel)
    except Exception as err:
        print(f"[!] Connection failed: {err}")
        print("[!] Tip: Start local broker with 'service rabbitmq-server start' or set RABBITMQ_URL.")
        print("[*] Running simulated dispatch log for verification:\n")
        run_simulated(duration_sec, interval_sec)
        return

    msg_seq = 0
    start_time = time.time()

    try:
        while time.time() - start_time < duration_sec:
            msg_seq += 1
            city = random.choice(CITIES)
            zone = random.choice(ZONES[city])
            req_type = random.choice(TYPES)

            # Every 10th message is a "poison pill" missing the required 'zone' field (Part D3)
            is_bad_msg = (msg_seq % 10 == 0)

            if is_bad_msg:
                routing_key = f"{city}.missing.{req_type}"
                payload = {
                    "id": f"REQ-{msg_seq:04d}",
                    "city": city,
                    # 'zone' is intentionally omitted!
                    "type": req_type,
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "is_malformed_test": True
                }
            else:
                routing_key = f"{city}.zone.{req_type}".replace(".zone.", f".{zone}.")
                payload = {
                    "id": f"REQ-{msg_seq:04d}",
                    "city": city,
                    "zone": zone,
                    "type": req_type,
                    "ts": datetime.now(timezone.utc).isoformat()
                }

            body = json.dumps(payload)
            channel.basic_publish(
                exchange=EXCHANGE_NAME,
                routing_key=routing_key,
                body=body,
                properties=pika.BasicProperties(content_type="application/json")
            )

            status_tag = "[POISON PILL - NO ZONE]" if is_bad_msg else "[OK]"
            print(f"[DISPATCH #{msg_seq:03d}] {status_tag:24s} Key: {routing_key:30s} -> Payload: {body}")
            time.sleep(interval_sec)

    except KeyboardInterrupt:
        print("\n[*] Dispatcher stopped by user.")
    finally:
        if 'connection' in locals() and connection.is_open:
            connection.close()
            print("[*] RabbitMQ connection cleanly closed.")


def run_simulated(duration_sec, interval_sec):
    """Fallback simulator printing exact routing events when broker is offline."""
    count = min(int(duration_sec / interval_sec), 25)
    for msg_seq in range(1, count + 1):
        city = random.choice(CITIES)
        zone = random.choice(ZONES[city])
        req_type = random.choice(TYPES)
        is_bad = (msg_seq % 10 == 0)

        if is_bad:
            routing_key = f"{city}.missing.{req_type}"
            body = {"id": f"REQ-{msg_seq:04d}", "city": city, "type": req_type, "ts": datetime.now(timezone.utc).isoformat(), "is_malformed": True}
        else:
            routing_key = f"{city}.{zone}.{req_type}"
            body = {"id": f"REQ-{msg_seq:04d}", "city": city, "zone": zone, "type": req_type, "ts": datetime.now(timezone.utc).isoformat()}

        status = "[POISON PILL - NO ZONE]" if is_bad else "[VALID]"
        print(f"[SIMULATED DISPATCH #{msg_seq:03d}] {status:24s} Key: {routing_key:30s} -> {json.dumps(body)}")
        time.sleep(0.1)


if __name__ == "__main__":
    dur = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    run_dispatcher(duration_sec=dur)

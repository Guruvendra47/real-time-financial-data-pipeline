# ==========================================
# IMPORT LIBRARIES
# ==========================================
import os
import json
from kafka import KafkaProducer
import websocket

# ==========================================
# CONFIG
# WHY:
# Keep secrets and environment-specific values out of source code.
# ==========================================
API_KEY = os.getenv("FINNHUB_API_KEY")
if not API_KEY:
    raise ValueError("Missing FINNHUB_API_KEY in environment variables")

WS_URL = f"wss://ws.finnhub.io?token={API_KEY}"

KAFKA_BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "trades")

SYMBOLS = os.getenv("SYMBOLS", "AAPL,TSLA,MSFT,BINANCE:BTCUSDT").split(",")

# ==========================================
# KAFKA PRODUCER
# WHY:
# Producer sends trade events to Kafka for downstream Spark processing.
# ==========================================
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    acks="all",
    retries=5,
    linger_ms=50
)

# ==========================================
# CALLBACKS
# ==========================================
def on_open(ws):
    print("Connection opened")

    # WHY:
    # Subscribe to each symbol so Finnhub sends live trade events.
    for symbol in SYMBOLS:
        subscribe_message = {
            "type": "subscribe",
            "symbol": symbol.strip()
        }
        ws.send(json.dumps(subscribe_message))
        print(f"Subscribed to {symbol.strip()}")

def on_message(ws, message):
    data = json.loads(message)

    # WHY:
    # Finnhub sends heartbeat/ping messages, and we ignore them.
    if data.get("type") == "ping":
        return

    # WHY:
    # Trade messages contain a list of trade records.
    if data.get("type") == "trade":
        for trade in data.get("data", []):
            print("Sending to Kafka:", trade)
            producer.send(KAFKA_TOPIC, trade)

        # WHY:
        # Flush here so messages are pushed promptly during live streaming.
        producer.flush()

def on_error(ws, error):
    print("Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("Connection closed")
    producer.flush()
    producer.close()

# ==========================================
# MAIN
# WHY:
# This keeps the websocket client running continuously.
# ==========================================
if __name__ == "__main__":
    print("Starting WebSocket client...")

    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    ws.run_forever()
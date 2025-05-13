from faker import Faker
from kafka import KafkaProducer
import json
import random
import time

fake = Faker()

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',  # Adjust if needed
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

TOPIC = 'transactions'

def generate_transaction():
    return {
        "transaction_id": fake.uuid4(),
        "user_id": fake.uuid4(),
        "merchant_id": fake.uuid4(),
        "amount": round(random.uniform(5, 2000), 2),
        "age": random.randint(18, 70),
        "gender": random.choice([0, 1]),
        "location_score": round(random.uniform(0, 1), 2),
        "transaction_hour": random.randint(0, 23),
        "device_score": round(random.uniform(0, 1), 2),
        "is_international": random.choice([True, False]),
        "has_vpn": random.choice([True, False]),
        "is_proxy": random.choice([True, False])
    }

if __name__ == "__main__":
    print(f"Producing messages to Kafka topic: {TOPIC}")
    while True:
        transaction = generate_transaction()
        producer.send(TOPIC, transaction)
        print(f"Sent: {transaction}")
        time.sleep(1)  # 1 transaction per second (adjust as needed)
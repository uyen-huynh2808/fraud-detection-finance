from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, IntegerType, DoubleType
from kafka import KafkaProducer
import json
import logging

# Kafka topic for fraud alerts
ALERT_TOPIC = "alerts"

# Define the schema for prediction messages
schema = StructType() \
    .add("transaction_id", StringType()) \
    .add("user_id", StringType()) \
    .add("merchant_id", StringType()) \
    .add("amount", DoubleType()) \
    .add("age", IntegerType()) \
    .add("gender", IntegerType()) \
    .add("location_score", DoubleType()) \
    .add("transaction_hour", IntegerType()) \
    .add("device_score", DoubleType()) \
    .add("prediction", IntegerType())

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Function to send alerts
def send_alert_batch(producer, batch_alerts):
    try:
        for alert_msg in batch_alerts:
            logger.info(f"Sending alert: {alert_msg}")
            producer.send(ALERT_TOPIC, json.dumps(alert_msg).encode("utf-8"))
        producer.flush()
        logger.info(f"Sent {len(batch_alerts)} alerts to topic '{ALERT_TOPIC}'")
    except Exception as e:
        logger.error(f"Error sending alert batch: {e}")

# Function to process each micro-batch
def process_batch(batch_df, batch_id):
    logger.info(f"Processing batch ID: {batch_id}")

    fraud_rows = batch_df.filter(col("prediction") == 1).collect()
    
    if not fraud_rows:
        logger.info("No fraud alerts in this batch.")
        return

    logger.info(f"Found {len(fraud_rows)} fraud alerts in this batch")

    batch_alerts = [
        {
            "transaction_id": row["transaction_id"],
            "user_id": row["user_id"],
            "merchant_id": row["merchant_id"],
            "amount": row["amount"],
            "alert": "FRAUD DETECTED"
        }
        for row in fraud_rows
    ]

    send_alert_batch(producer, batch_alerts)

# MAIN
if __name__ == "__main__":
    logger.info("Starting Fraud Alert Producer...")

    spark = SparkSession.builder.appName("FraudAlertProducer").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    producer = KafkaProducer(bootstrap_servers="localhost:9092")

    raw_stream_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "predictions") \
        .option("startingOffsets", "latest") \
        .load()

    json_df = raw_stream_df.selectExpr("CAST(value AS STRING) as json_string")
    parsed_df = json_df.select(from_json(col("json_string"), schema).alias("data")).select("data.*")

    query = parsed_df.writeStream \
        .foreachBatch(lambda df, id: process_batch(df, id)) \
        .option("checkpointLocation", "./checkpoints/alerts") \
        .start()

    query.awaitTermination()
    producer.close()
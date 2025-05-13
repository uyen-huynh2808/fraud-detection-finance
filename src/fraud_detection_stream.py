from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, struct, to_json
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, BooleanType
from pyspark.ml import PipelineModel

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("FraudDetectionStream") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Define schema matching training features
schema = StructType([
    StructField("transaction_id", StringType(), True),
    StructField("user_id", StringType(), True),
    StructField("merchant_id", StringType(), True),
    StructField("amount", DoubleType(), True),
    StructField("age", IntegerType(), True),
    StructField("gender", IntegerType(), True),
    StructField("location_score", DoubleType(), True),
    StructField("transaction_hour", IntegerType(), True),
    StructField("device_score", DoubleType(), True),
    StructField("is_international", BooleanType(), True),
    StructField("has_vpn", BooleanType(), True),
    StructField("is_proxy", BooleanType(), True)
])

# Read from Kafka topic "transactions"
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "transactions") \
    .option("startingOffsets", "latest") \
    .load()

# Parse JSON from Kafka messages
json_df = kafka_df.selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json(col("json_str"), schema).alias("data")) \
    .select("data.*")

# Extract features for model input 
features_df = json_df.select("amount", "location_score", "transaction_hour", "device_score", "is_international", "has_vpn", "is_proxy")

# Load saved model
model = PipelineModel.load("models/fraud_model.pkl")

# Run predictions
predictions = model.transform(json_df)

# Cast prediction to IntegerType for consistency
predictions = predictions.withColumn("prediction", col("prediction").cast("integer"))

# Final DataFrame to use for writing
final_df = predictions.select("*")  # or select specific fields

# Write full prediction output to Kafka topic "predictions"
final_df.select(to_json(struct(
    "transaction_id", "user_id", "merchant_id", "amount", "age",
    "gender", "location_score", "transaction_hour", "device_score", "prediction"
)).alias("value")) \
    .writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("topic", "predictions") \
    .option("checkpointLocation", "/mnt/d/PATH_TO/checkpoints/predictions") \
    .outputMode("append") \
    .start()

# Also print selected output to console
query = final_df.select("transaction_id", "amount", "age", "prediction") \
    .writeStream \
    .outputMode("append") \
    .format("console") \
    .option("checkpointLocation", "/mnt/d/PATH_TO/checkpoints/console") \
    .start()

query.awaitTermination()
from faker import Faker
import random
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, BooleanType
from pyspark.sql.utils import AnalysisException
from pyspark.ml.util import MLWriter
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import BinaryClassificationEvaluator
import os
import shutil
import datetime

# Step 1: Create Spark Session
spark = SparkSession.builder \
    .appName("FraudModelRetrain") \
    .config("spark.driver.memory", "4g") \
    .config("spark.sql.shuffle.partitions", "10") \
    .getOrCreate()

# Set log level to WARN to reduce verbosity
spark.sparkContext.setLogLevel("WARN")

# Step 2: Generate Synthetic Data
fake = Faker()

def generate_transaction():
    amount = round(random.uniform(5, 2000), 2)
    age = random.randint(18, 70)
    gender = random.choice([0, 1])
    location_score = round(random.uniform(0, 1), 2)
    transaction_hour = random.randint(0, 23)
    device_score = round(random.uniform(0, 1), 2)
    is_international = random.choice([True, False])
    has_vpn = random.choice([True, False])
    is_proxy = random.choice([True, False])

    fraud_risk = 0.01
    if amount > 1500: fraud_risk += 0.2
    if is_international: fraud_risk += 0.2
    if has_vpn or is_proxy: fraud_risk += 0.3
    if location_score < 0.2: fraud_risk += 0.1
    if device_score < 0.2: fraud_risk += 0.1
    if transaction_hour < 6 or transaction_hour > 22: fraud_risk += 0.1

    is_fraud = int(random.random() < fraud_risk)

    return {
        "transaction_id": fake.uuid4(),
        "user_id": fake.uuid4(),
        "merchant_id": fake.uuid4(),
        "amount": amount,
        "age": age,
        "gender": gender,
        "location_score": location_score,
        "transaction_hour": transaction_hour,
        "device_score": device_score,
        "is_international": is_international,
        "has_vpn": has_vpn,
        "is_proxy": is_proxy,
        "is_fraud": is_fraud
    }

data = [generate_transaction() for _ in range(100_000)]

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
    StructField("is_proxy", BooleanType(), True),
    StructField("is_fraud", IntegerType(), True)
])

df = spark.createDataFrame(data, schema)

# Step 2.5: Load historical data if it exists
historical_path = "/PATH_TO_airflow_home/data/historical_transactions.parquet"

if os.path.exists(historical_path):
    try:
        old_df = spark.read.parquet(historical_path)
        print(f"Loaded {old_df.count()} rows from historical data.")

        # OPTIONAL: Keep both old + new in memory if needed for training later
        df_for_model = df.union(old_df)

    except AnalysisException as e:
        print(f"Error reading historical data: {e}")
        df_for_model = df
    except Exception as e:
        print(f"Unexpected error during loading historical data: {e}")
        df_for_model = df
else:
    df_for_model = df

# Write only the new batch to the historical store
if not df.rdd.isEmpty():
    df.write.mode("append").parquet(historical_path)
    print(f"Appended {df.count()} rows to: {historical_path}")
else:
    print("No new data to append.")

# Step 3: Prepare Features
feature_cols = ["amount", "location_score", "transaction_hour", "device_score", "is_international", "has_vpn", "is_proxy"]
assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
rf = RandomForestClassifier(featuresCol="features", labelCol="is_fraud", numTrees=50)
pipeline = Pipeline(stages=[assembler, rf])

# Step 4: Train/Test Split
train_df, test_df = df.randomSplit([0.8, 0.2], seed=42)

# Step 5: Train Model
model = pipeline.fit(train_df)

# Step 6: Evaluate
predictions = model.transform(test_df)
evaluator = BinaryClassificationEvaluator(labelCol="is_fraud")
auc = evaluator.evaluate(predictions)
print(f"Test AUC: {auc:.4f}")

# Step 7: Save Model
model_path = "/mnt/d/PATH_TO/models/fraud_model.pkl"
model.write().overwrite().save(model_path)
print(f"Model saved at: {model_path}")

# Stop Spark
spark.stop()
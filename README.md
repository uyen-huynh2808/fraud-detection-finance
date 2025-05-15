# Real-Time Fraud Detection in Finance (Apache Spark - Apache Kafka - PySpark ML)

## Overview

This project simulates a **real-time fraud detection and alerting pipeline** in the financial domain using a big data ecosystem. It generates synthetic transaction data using **Faker**, streams it through **Kafka**, processes it with **Apache Spark Structured Streaming**, and detects fraudulent activity using a **PySpark ML model**. When a suspicious transaction is identified, an alert message is sent to users in real-time through a **Kafka fraud alert topic**. The pipeline is fully automated: real-time data is ingested and processed using **Kafka** and **Spark**, while **Apache Airflow** is used to orchestrate periodic model retraining.

## Project Goals

- **Simulate Real-Time Financial Transactions:**  
  Generate realistic synthetic transaction data using `Faker`, covering users, merchants, transaction metadata, and potential fraud indicators.

- **Implement Streaming Architecture:**  
  Build a real-time data pipeline using **Kafka** to ingest continuous transaction streams and **Apache Spark Structured Streaming** for scalable processing.

- **Detect Fraudulent Behavior:**  
  Apply machine learning models with **PySpark ML** to detect anomalies and classify transactions as fraudulent or legitimate in near real-time.

- **Send Real-Time Fraud Alerts:**  
  Deliver instant fraud notifications to downstream services or users through a dedicated **Kafka alert topic** by sending emails, allowing for real-time response without the need for data storage or reporting tools.

- **Orchestrate with Airflow:**  
  Automate model training and deployment using Apache Airflow, ensuring scalability, maintainability, and daily retraining.

## Architecture

![Architecture](https://github.com/user-attachments/assets/51506e72-e46f-4f23-9cff-ebe44ca4f234)

> **Note:**
> - The fraud detection model is retrained daily using historical data plus 100,000 new synthetic records generated with Faker.
> - Retraining is automated with Apache Airflow, and the updated model is saved as `fraud_model.pkl`.
> - After each retraining, the used data is added to the historical dataset for future training.
> - In streaming, Spark ML only loads and applies the latest model — it does not retrain in real time.

## Technology Stack

| Component              | Tool / Framework             |
|------------------------|------------------------------|
| Data Generation        | Faker                        |
| Messaging              | Apache Kafka                 |
| Streaming Engine       | Apache Spark (Structured Streaming) |
| Machine Learning       | PySpark ML                |
| Model Retraining Orchestration | Apache Airflow               |
| Real-Time Alerts       | Kafka Alert Topic            |

## Data Used

This project uses synthetic financial transaction data generated via the Faker Python library. The data simulates realistic behavior of users, merchants, and transactions — mimicking real-world online payment and banking activity — but does not include any actual private or sensitive user information.

Faker continuously generates streaming data that mimics:

- Customers making payments

- Merchant identifiers

- Risk-related metadata: age, gender, VPN/proxy usage, international flag

- Transaction characteristics: amount, transaction hour, location and device scores

> **Note:**  
> Each day, 100,000 new synthetic transactions (balanced for fraud and legitimate cases) are generated and combined with stored historical data to train the model with PySpark ML. The combined dataset is then archived as historical data for the next retraining cycle.

## Data Model

### Kafka Topic: `transactions`

Each message published to this topic represents a **simulated financial transaction** generated using the `faker` library. The structure matches the schema used by the PySpark stream and the ML pipeline.

**Schema Fields**

| Field              | Type     | Description                                                                 |
|-------------------|----------|-----------------------------------------------------------------------------|
| `transaction_id`   | STRING   | Unique identifier for each transaction (`fake.uuid4()`)                     |
| `user_id`          | STRING   | Simulated user ID (`fake.uuid4()`)                                          |
| `merchant_id`      | STRING   | Simulated merchant ID (`fake.uuid4()`)                                      |
| `amount`           | DOUBLE   | Transaction amount in USD (range: 5 to 2000)                                |
| `age`              | INTEGER  | User age (range: 18–70)                                                     |
| `gender`           | INTEGER  | Encoded gender (0 = female, 1 = male)                                       |
| `location_score`   | DOUBLE   | Score indicating the user's geographic risk (range: 0.0–1.0)                |
| `transaction_hour` | INTEGER  | Hour of the day the transaction occurs (0–23)                               |
| `device_score`     | DOUBLE   | Trustworthiness of the device (range: 0.0–1.0)                              |
| `is_international` | BOOLEAN  | Whether the transaction is cross-border                                    |
| `has_vpn`          | BOOLEAN  | Whether the user was using a VPN during the transaction                    |
| `is_proxy`         | BOOLEAN  | Whether the connection used a proxy                                        |
| `is_fraud`         | INTEGER  | Fraud label (1 = fraudulent, 0 = normal); used for training/testing         |

> **Notes:**  
> - This is a **flat message schema**, combining transaction, user, and device context in one payload.
> - `user_id` and `merchant_id` are designed to support future relational joins (e.g., with `user_info_stream` and `merchant_info_stream` if modeled later).
> - The `is_fraud` field is primarily for training/testing and may be excluded in real-time fraud inference use cases.

### Kafka Topic: `predictions`

This Kafka topic is used to publish fraud detection model predictions. It includes transaction data along with the predicted fraud label.

**Schema Fields**

| Field              | Type     | Description                                                                 |
|--------------------|----------|-----------------------------------------------------------------------------|
| `transaction_id`    | STRING   | Unique identifier for each transaction (`fake.uuid4()`)                     |
| `user_id`           | STRING   | Simulated user ID (`fake.uuid4()`)                                          |
| `merchant_id`       | STRING   | Simulated merchant ID (`fake.uuid4()`)                                      |
| `amount`            | DOUBLE   | Transaction amount in USD (range: 5 to 2000)                                |
| `age`               | INTEGER  | User age (range: 18–70)                                                     |
| `gender`            | INTEGER  | Encoded gender (0 = female, 1 = male)                                       |
| `location_score`    | DOUBLE   | Score indicating the user's geographic risk (range: 0.0–1.0)                |
| `transaction_hour`  | INTEGER  | Hour of the day the transaction occurs (0–23)                               |
| `device_score`      | DOUBLE   | Trustworthiness of the device (range: 0.0–1.0)                              |
| `prediction`   | INTEGER  | Fraud prediction: 1 = fraud, 0 = not fraud  

### Kafka Topic: `alerts`

This Kafka topic is used to publish alerts when a fraud is detected. If a fraud is predicted, an alert message is sent to this topic.

**Schema Fields**

| Field              | Type     | Description                                                                 |
|--------------------|----------|-----------------------------------------------------------------------------|
| `transaction_id`    | STRING   | Unique identifier for each transaction (`fake.uuid4()`)                     |
| `user_id`           | STRING   | Simulated user ID (`fake.uuid4()`)                                          |
| `merchant_id`       | STRING   | Simulated merchant ID (`fake.uuid4()`)                                      |
| `amount`            | DOUBLE   | Transaction amount in USD (range: 5 to 2000)                                |
| `alert`             | STRING   | Fraud alert message (e.g., "FRAUD DETECTED")                               

## Project Files

1. `config/kafka_config.json` – Kafka topic and broker configuration.  
2. `config/spark_config.yaml` – Spark app settings, including checkpointing and batch configs. 
3. `src/train_model.py` – Train the model with historical + 100,000 new records, saves it, and updates historical data.  
4. `models/fraud_model.pkl` – Serialized trained PySpark model for reuse in streaming pipeline.
5. `src/faker_producer.py` – Produces synthetic transaction data using Faker and streams it into Kafka.   
6. `src/fraud_detection_stream.py` – Spark Structured Streaming pipeline to detect fraud in real-time using ML model.
7. `src/fraud_alert_producer.py` – Sends real-time fraud alerts to a dedicated Kafka alert topic when fraud is detected.
8. `src/fraud_alert_consumer.py` – Subscribes to the alert topic and:
    - Logs alert in terminal (for testing/demo).
    - Sends email to a configured user (for realism).
9. `dags/training_pipeline.py` – Airflow DAG to automate periodic retraining and deployment of the model.
10. `notebooks/pipeline_walkthrough.ipynb` – Interactive guide for executing key components of the real-time fraud detection pipeline.

## License

This project is for educational and demo purposes only. All transaction data is artificially generated using Faker and does not represent any real individuals or businesses.

## Conclusion

- This project demonstrates a fully integrated, real-time fraud detection pipeline using Apache Kafka, Apache Spark Structured Streaming, and PySpark ML.

- Synthetic financial transactions are generated using Faker, streamed via Kafka, and evaluated in real-time using a pre-trained machine learning model.

- Detected frauds are immediately communicated through a Kafka alert topic, with optional email notifications for end-user visibility.

- Apache Airflow automates daily retraining of the model, ensuring the system adapts to new fraud patterns over time.

- The architecture showcases key data engineering skills in streaming, orchestration, ML integration, and alerting—forming a robust blueprint for real-world fintech use cases.

----

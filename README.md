# Real-Time Fraud Detection in Finance (Apache Spark - Apache Kafka - PySpark MLlib)

## Overview

This project simulates a **real-time fraud detection and alerting pipeline** in the financial domain using a big data ecosystem. It generates synthetic transaction data using **Faker**, streams it through **Kafka**, processes it with **Apache Spark Structured Streaming**, and detects fraudulent activity using a **PySpark ML model**. When a suspicious transaction is identified, an alert message is sent to users in real-time through a **Kafka fraud alert topic**. The pipeline is fully automated and orchestrated using **Apache Airflow**, including periodic model retraining and deployment.

## Project Goals

- **Simulate Real-Time Financial Transactions:**  
  Generate realistic synthetic transaction data using `Faker`, covering users, merchants, transaction metadata, and potential fraud indicators.

- **Implement Streaming Architecture:**  
  Build a real-time data pipeline using **Kafka** to ingest continuous transaction streams and **Apache Spark Structured Streaming** for scalable processing.

- **Detect Fraudulent Behavior:**  
  Apply machine learning models with **PySpark MLlib** to detect anomalies and classify transactions as fraudulent or legitimate in near real-time.

- **Send Real-Time Fraud Alerts:**  
  Deliver immediate fraud notifications to downstream services or users via a dedicated **Kafka alert topic**, enabling real-time response without relying on data storage or reporting tools.

- **Orchestrate with Airflow:**  
  Automate model training, deployment, and streaming workflows using **Apache Airflow** to ensure scalability, maintainability, and periodic retraining.

## Architecture

![Architecture](https://github.com/user-attachments/assets/c9d5fcc9-ea5d-4779-836f-74262f9645a3)

> **Note:**  In the streaming pipeline, **Spark MLlib only loads and applies the pre-trained model** — it does **not** retrain it in real-time.

## Technology Stack

| Component              | Tool / Framework             |
|------------------------|------------------------------|
| Data Generation        | Faker                        |
| Messaging              | Apache Kafka                 |
| Streaming Engine       | Apache Spark (Structured Streaming) |
| Machine Learning       | PySpark MLlib                |
| Workflow Orchestration | Apache Airflow               |
| Real-Time Alerts       | Kafka Alert Topic            |

## Data Used

This project uses synthetic financial transaction data generated via the **Faker** Python library. The data simulates realistic behavior of users, merchants, and transactions — mimicking real-world online payment and banking activity — but does not include any actual private or sensitive user information.

Faker continuously generates streaming data that mimics:

- Customers making payments  
- Merchant identifiers  
- Timestamps and transaction metadata  
- Legitimate vs. fraudulent behavior patterns

> **Note:**  
> A batch of synthetic data (e.g., 50,000–100,000 rows) is generated offline using Faker and used to train the initial fraud detection model. This ensures the model has a labeled dataset with a balanced mix of legitimate and fraudulent transactions for accurate learning. Once deployed, the model can be periodically retrained using historical data collected from the real-time stream.

## Data Model

### Kafka Topics (Streamed Data)

**transaction_stream**  
- `transaction_id`: Unique transaction ID  
- `user_id`: Reference to the user making the transaction  
- `merchant_id`: Reference to the merchant  
- `timestamp`: Time of transaction  
- `amount`: Transaction amount  
- `currency`: Currency used  
- `device_ip`: Device IP address  
- `is_fraud`: Fraud label (true/false)  

**user_info_stream**  
- `user_id`: Unique user ID  
- `age`: Age of user  
- `gender`: Gender  
- `location`: User location  
- `signup_date`: User registration date  

**merchant_info_stream**  
- `merchant_id`: Unique merchant ID  
- `name`: Merchant name  
- `category`: Business category  
- `location`: Merchant location  
- `created_at`: Merchant onboarding date  

## Project Files

1. `src/train_model.py` – Script to train the fraud detection model using PySpark ML on historical (simulated) data.  
2. `models/fraud_model.pkl` – Serialized trained PySpark model for reuse in streaming pipeline.
3. `src/faker_producer.py` – Produces synthetic transaction data using Faker and streams it into Kafka.  
4. `config/kafka_config.json` – Kafka topic and broker configuration.  
5. `config/spark_config.yaml` – Spark app settings, including checkpointing and batch configs.  
6. `src/fraud_detection_stream.py` – Spark Structured Streaming pipeline to detect fraud in real-time using ML model.
7. `src/fraud_alert_producer.py` – Sends real-time fraud alerts to a dedicated Kafka alert topic when fraud is detected.
8. `src/fraud_alert_consumer.py` – Consumes fraud alerts for downstream services (e.g., notifications, logging).  
9. `dags/training_pipeline.py` – Airflow DAG to automate periodic retraining and deployment of the model.  

## License

This project is for educational and demo purposes only. All transaction data is artificially generated using Faker and does not represent any real individuals or businesses.

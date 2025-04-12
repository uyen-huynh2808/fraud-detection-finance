# Real-Time Fraud Detection in Finance (Apache Spark - Apache Kafka - Power BI)

## Overview

This project simulates a **real-time fraud detection pipeline** in the financial domain using a big data ecosystem. It generates synthetic transaction data using **Faker**, streams it through **Kafka**, processes it with **Apache Spark Structured Streaming**, detects fraud using a **PySpark ML model**, and visualizes suspicious activity in **Power BI**. The entire pipeline is orchestrated with **Airflow**.

## Project Goals

- **Simulate Real-Time Financial Transactions:**  
  Generate realistic synthetic transaction data using `Faker`, covering users, merchants, transaction metadata, and potential fraud indicators.

- **Implement Streaming Architecture:**  
  Build a real-time data pipeline using **Kafka** to ingest continuous transaction streams and **Apache Spark Structured Streaming** for scalable processing.

- **Detect Fraudulent Behavior:**  
  Apply machine learning models with **PySpark MLlib** to detect anomalies and classify transactions as fraudulent or legitimate in near real-time.

- **Visualize Key Insights:**  
  Provide a dynamic **Power BI dashboard** showing fraud alerts, high-risk users or merchants, transaction heatmaps, and financial trends.

- **Orchestrate with Airflow:**  
  Automate model training, batch scoring, and data workflows using **Apache Airflow** to ensure reliability and retrainability.

## Architecture

![Architecture](https://github.com/user-attachments/assets/7bf25abe-665f-42e4-a015-d39458328d32)

> This architecture shows the end-to-end data flow for a real-time fraud detection pipeline using Faker for synthetic data, Kafka for ingestion, Spark for processing and ML, MySQL for storage, and Power BI for visualization. Airflow orchestrates the training and streaming workflows.

## Technology Stack

| Component              | Tool / Framework             |
|------------------------|------------------------------|
| Data Generation        | Faker                        |
| Messaging              | Apache Kafka                 |
| Streaming Engine       | Apache Spark (Structured Streaming) |
| Machine Learning       | PySpark MLlib                |
| Workflow Orchestration | Apache Airflow               |
| Data Storage           | MySQL                        |
| Visualization          | Power BI                     |

> **Note:** Kafka can be used for real-time consumers, but **Power BI works better with SQL-based storages like MySQL** for reporting and dashboarding.

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

### Fact Table

**fact_transactions**
- `transaction_id`: Unique transaction ID  
- `user_id`: Reference to the user making the transaction  
- `merchant_id`: Reference to the merchant  
- `timestamp`: Time of transaction  
- `amount`: Transaction amount  
- `currency`: Currency used  
- `device_ip`: Device IP address  
- `is_fraud`: Fraud label (true/false)  

### Dimension Tables

**dim_users**
- `user_id`: Unique user ID  
- `age`: Age of user  
- `gender`: Gender  
- `location`: User location  
- `signup_date`: User registration date  

**dim_merchants**
- `merchant_id`: Unique merchant ID  
- `name`: Merchant name  
- `category`: Business category  
- `location`: Merchant location  
- `created_at`: Merchant onboarding date  

(ADD ER DIAGRAM)

## Project Files

1. `src/train_model.py` – Script to train the fraud detection model using PySpark ML on historical (simulated) data.  
2. `models/fraud_model.pkl` – Serialized trained PySpark model for reuse in streaming pipeline.
3. `src/faker_producer.py` – Produces synthetic transaction data using Faker and streams it into Kafka.  
4. `config/kafka_config.json` – Kafka topic and broker configuration.  
5. `config/spark_config.yaml` – Spark app settings, including checkpointing and batch configs.  
6. `src/fraud_detection_stream.py` – Spark Structured Streaming pipeline to detect fraud in real-time using ML model. 
7. `schema/mysql_schema.sql` – SQL script to create the `fact_transactions`, `dim_users`, and `dim_merchants` tables in MySQL. 
8. `dags/training_pipeline.py` – Airflow DAG to automate periodic retraining and deployment of the model.  
9. `dashboards/fraud_dashboard.pbix` – Power BI report to visualize fraud detection metrics and transaction activity.  

## License

This project is for educational and demo purposes only. All transaction data is artificially generated using Faker and does not represent any real individuals or businesses.

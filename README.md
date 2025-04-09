# Real-Time Fraud Detection in Finance using Apache Spark & Kafka

## Overview

This project demonstrates a complete pipeline for **real-time fraud detection** in the financial domain using **Big Data technologies**. It simulates live transaction data using `Faker`, streams the data with `Kafka`, processes it with `Apache Spark Structured Streaming`, and uses `PySpark MLlib` to classify transactions as fraudulent or not.

The project includes orchestration with `Airflow` and visualization with `Power BI`.

---

## Objectives

- Simulate financial transaction streams using `Faker`.
- Detect fraudulent transactions using a machine learning model in `PySpark`.
- Process streaming data with low latency using `Kafka` and `Spark`.
- Visualize fraud detection metrics in a BI dashboard.
- Schedule model training and pipeline tasks with `Airflow`.

---

## Architecture

Faker → Kafka → Spark Streaming → ML Model → Kafka / PostgreSQL → Power BI ↑ Airflow

fraud-detection/
│
├── data_generator/
│   └── faker_producer.py          # Simulates transactions and streams to Kafka
│
├── spark_streaming/
│   └── fraud_detection_stream.py  # Spark Structured Streaming + ML model
│
├── airflow_dags/
│   └── training_pipeline.py       # Airflow DAG for model training
│
├── model/
│   └── train_model.py             # ML model training with PySpark
│
├── dashboards/
│   └── fraud_dashboard.pbix       # Power BI dashboard
│
├── requirements.txt
└── README.md




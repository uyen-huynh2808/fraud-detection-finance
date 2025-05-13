from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import subprocess
import os

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

def check_previous_model():
    model_path = "/mnt/d/PATH_TO/models/fraud_model.pkl"
    if os.path.exists(model_path):
        print("Previous model found. Will be overwritten during retraining.")
    else:
        print("No existing model found. Training from scratch.")

def retrain_model():
    subprocess.run(["python", "/mnt/d/PATH_TO/src/train_model.py"], check=True)
    print("Model retrained and saved.")

def deploy_model():
    print("Model is in place. No separate deployment step needed.")

with DAG(
    dag_id="fraud_model_training_pipeline",
    default_args=default_args,
    description="Periodic model retraining pipeline using historical data",
    schedule="0 0 * * *",
    start_date=datetime(YOUR_DATE),
    catchup=False,
    tags=["fraud", "ml", "training"]
) as dag:

    t1 = PythonOperator(
        task_id="check_previous_model",
        python_callable=check_previous_model,
    )

    t2 = PythonOperator(
        task_id="retrain_model",
        python_callable=retrain_model,
    )

    t3 = PythonOperator(
        task_id="deploy_model",
        python_callable=deploy_model,
    )

    t1 >> t2 >> t3
import json
import logging
from kafka import KafkaConsumer
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Configuration
ALERT_TOPIC = "alerts"
BOOTSTRAP_SERVERS = "localhost:9092"

# Hardcoded credentials
SENDGRID_API_KEY = "YOUR_API_KEY"
TO_EMAIL = "ALERT_EMAIL_TO"
FROM_EMAIL = "ALERT_EMAIL_FROM"  # Prefer using a verified sender in SendGrid

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Send email using SendGrid
def send_email_alert(alert_data):
    try:
        subject = f"FRAUD ALERT: Transaction {alert_data['transaction_id']}"
        content = f"""
        FRAUD DETECTED!
        Transaction ID: {alert_data['transaction_id']}
        User ID: {alert_data['user_id']}
        Merchant ID: {alert_data['merchant_id']}
        Amount: ${alert_data['amount']:.2f}
        """
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=TO_EMAIL,
            subject=subject,
            plain_text_content=content
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        logger.info(f"Email sent. Status code: {response.status_code}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

# Main Kafka consumer logic
def main():
    logger.info("Starting Fraud Alert Consumer...")

    consumer = KafkaConsumer(
        ALERT_TOPIC,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        auto_offset_reset="latest",
        enable_auto_commit=True,
        value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )

    for message in consumer:
        alert = message.value
        logger.info(f"Received fraud alert: {alert}")
        send_email_alert(alert)

if __name__ == "__main__":
    main()
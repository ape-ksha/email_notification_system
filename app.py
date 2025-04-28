from flask import Flask, request, jsonify
import pika
from db import SessionLocal
from models import Email, Base
from config import RABBITMQ_URL, engine

app = Flask(__name__)

# Create tables
Base.metadata.create_all(bind=engine)

# Connect to RabbitMQ
params = pika.URLParameters(RABBITMQ_URL)
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue='email_queue')

@app.route('/send-email', methods=['POST'])
def send_email():
    data = request.json
    session = SessionLocal()
    
    # Save to DB
    email = Email(
        to_address=data['to'],
        subject=data['subject'],
        body=data['body']
    )
    session.add(email)
    session.commit()

    # Publish to RabbitMQ
    channel.basic_publish(
        exchange='',
        routing_key='email_queue',
        body=str(email.id)
    )

    session.close()
    return jsonify({'message': 'Email queued', 'email_id': email.id})

if __name__ == "__main__":
    app.run(debug=True)

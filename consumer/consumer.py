# consumer.py
import os
from dotenv import load_dotenv
from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError
import psycopg2

# Load environment variables from .env file
load_dotenv()

# Set the path to your service account key file
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'key1.json'

# Retrieve environment variables
project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
subscription_id = 'my-subscription'
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')

# Debug: Print the values of the environment variables
print(f"GOOGLE_CLOUD_PROJECT: {project_id}")
print(f"GOOGLE_APPLICATION_CREDENTIALS: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")
print(f"DB_HOST: {db_host}")
print(f"DB_USER: {db_user}")
print(f"DB_PASSWORD: {db_password}")
print(f"DB_NAME: {db_name}")

# Initialize the Pub/Sub client
subscriber = pubsub_v1.SubscriberClient()

# Define the subscription path
subscription_path = subscriber.subscription_path(project_id, subscription_id)

# Establish a connection to the PostgreSQL database
conn = psycopg2.connect(
    host=db_host,
    database=db_name,
    user=db_user,
    password=db_password
)
cursor = conn.cursor()

conn.commit()

# Callback function to handle incoming messages
def callback(message):
    print(f"Received message: {message.data.decode('utf-8')}")
    try:
        # Insert the received message into the database
        cursor.execute('INSERT INTO message (content) VALUES (%s)', (message.data.decode('utf-8'),))
        conn.commit()
        message.ack()
        print("Message saved to database and acknowledged.")
    except Exception as e:
        print(f"Failed to save message to database: {e}")
        conn.rollback()

# Subscribe to the topic
streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}...\n")

# Keep the main thread alive to listen for messages
try:
    streaming_pull_future.result()
except TimeoutError:
    streaming_pull_future.cancel()

# Close the database connection
cursor.close()
conn.close()

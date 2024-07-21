import os
from dotenv import load_dotenv
from google.cloud import pubsub_v1

# Load environment variables from .env file
load_dotenv()

# Set the path to your service account key file
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'key1.json'

# Retrieve environment variables
project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
topic_id = 'my-topic'

# Initialize the Pub/Sub client
publisher = pubsub_v1.PublisherClient()

# Define the topic path
topic_path = publisher.topic_path(project_id, topic_id)

def publish_message(message):
    try:
        future = publisher.publish(topic_path, message.encode('utf-8'))
        print(f"Published message ID: {future.result()}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    publish_message('Hello, world!')

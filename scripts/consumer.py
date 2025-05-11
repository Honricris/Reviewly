from kafka import KafkaConsumer
import json
import requests
import time
from collections import defaultdict

# Initialize Kafka consumer
print("Initializing Kafka consumer...")
consumer = KafkaConsumer(
    bootstrap_servers=['localhost:29092'],
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    auto_offset_reset='earliest',
    group_id='reviewly-consumer-group'
)
print("Kafka consumer initialized successfully.")

# Backend API settings
BASE_URL = 'http://localhost:5000/api/v0'
PRODUCTS_ENDPOINT = f'{BASE_URL}/products/'
REVIEWS_ENDPOINT = f'{BASE_URL}/reviews/'
JWT_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyNyIsImVtYWlsIjoiaG9ucmljcmlzQGdtYWlsLmNvbSIsImdpdGh1Yl9pZCI6bnVsbCwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzQ3MTM0NTczfQ.3WlsTdLX2yMJx6_k82evoqM3w-2Ch6nrJ4O-vvWdXmE'  

# Headers for API requests
headers = {
    'Authorization': f'Bearer {JWT_TOKEN}',
    'Content-Type': 'application/json'
}
print(f"API headers set: {headers}")

# Function to get product_id by parent_asin
def get_product_id_by_parent_asin(parent_asin):
    print(f"Querying product_id for parent_asin: {parent_asin}")
    try:
        response = requests.get(
            f'{PRODUCTS_ENDPOINT}?parent_asin={parent_asin}',
            headers=headers
        )
        print(f"GET {PRODUCTS_ENDPOINT}?parent_asin={parent_asin} returned status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            products = data.get('products', [])  
            print(f"Products response: {data}")
            if products:  
                product_id = products[0].get('product_id')
                print(f"Found product_id: {product_id} for parent_asin: {parent_asin}")
                return product_id
            else:
                print(f"No products found for parent_asin: {parent_asin}")
                return None
        else:
            print(f"Failed to query product. Status: {response.status_code}, Response: {response.text}")
            return None
    except requests.RequestException as e:
        print(f"Error querying product by parent_asin: {e}")
        return None

def process_products(consumer, timeout_seconds=10):
    """Process all product messages first until no more messages are available"""
    print("=== STARTING PRODUCTS PROCESSING PHASE ===")
    products_processed = set()
    
    # Subscribe only to products topic
    consumer.subscribe(['products'])
    
    # Set a timeout for how long to wait for new messages
    last_message_time = time.time()
    
    while True:
        # Poll for messages with a short timeout
        messages = consumer.poll(timeout_ms=1000)  # 1 second poll timeout
        
        if not messages:
            # No messages received
            if time.time() - last_message_time > timeout_seconds:
                print(f"No product messages received for {timeout_seconds} seconds, ending products processing")
                break
            continue
        
        for topic_partition, partition_messages in messages.items():
            for message in partition_messages:
                if message.topic != 'products':
                    continue
                    
                record = message.value
                parent_asin = record.get('parent_asin')
                print(f"Processing product: {parent_asin}")
                
                try:
                    print(f"Sending POST to {PRODUCTS_ENDPOINT} with payload: {json.dumps(record, indent=2)}")
                    response = requests.post(PRODUCTS_ENDPOINT, json=record, headers=headers)
                    print(f"POST {PRODUCTS_ENDPOINT} returned status: {response.status_code}")
                    
                    if response.status_code in [200, 201]:
                        products_processed.add(parent_asin)
                        print(f"Successfully processed product: {parent_asin}")
                    else:
                        print(f"Failed to process product: Status {response.status_code}, Response: {response.text}")
                    
                    time.sleep(0.1)
                    
                except requests.RequestException as e:
                    print(f"Error processing product: {e}")
                
                # Update last message time
                last_message_time = time.time()
    
    print("=== COMPLETED PRODUCTS PROCESSING PHASE ===")
    return products_processed

def process_reviews(consumer):
    """Process reviews for any product with a valid product_id"""
    print("=== STARTING REVIEWS PROCESSING PHASE ===")
    
    # Subscribe to reviews topic
    consumer.subscribe(['reviews'])
    
    for message in consumer:
        if message.topic != 'reviews':
            continue
            
        record = message.value
        parent_asin = record.get('parent_asin')
        print(f"Processing review for product: {parent_asin}")
        
        product_id = get_product_id_by_parent_asin(parent_asin)
        
        if not product_id:
            print(f"Could not find product_id for {parent_asin}, skipping review")
            continue
            
        review_payload = record.copy()
        review_payload['product_id'] = product_id
        
        try:
            print("\n=== SENDING REVIEW PAYLOAD ===")
            print(f"Endpoint: {REVIEWS_ENDPOINT}")
            print("Headers:", json.dumps(headers, indent=2))
            print("Payload:")
            print(json.dumps(review_payload, indent=2, ensure_ascii=False))
            print("=============================\n")
            
            response = requests.post(REVIEWS_ENDPOINT, json=review_payload, headers=headers)
            
            print("\n=== RECEIVED RESPONSE ===")
            print(f"Status Code: {response.status_code}")
            print("Response Body:")
            try:
                print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                print(response.text)
            print("=========================\n")
            
            if response.status_code not in [200, 201]:
                print(f"Failed to process review: Status {response.status_code}, Response: {response.text}")
                
            time.sleep(0.1)
            
        except requests.RequestException as e:
            print(f"Error processing review: {e}")
            print(f"Exception occurred with payload: {json.dumps(review_payload, indent=2)}")

if __name__ == "__main__":
    try:
        valid_products = process_products(consumer)
        
        process_reviews(consumer)
            
    except KeyboardInterrupt:
        print("Consumer stopped by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        consumer.close()
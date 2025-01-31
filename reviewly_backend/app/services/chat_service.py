import os
import requests
import time
from dotenv import load_dotenv
from flask import request

load_dotenv()

class EdenAIChatService:
    def __init__(self):
        self.api_url = os.getenv("EDEN_API_URL")
        self.headers = {
            "Authorization": f"Bearer {os.getenv('EDEN_API_TOKEN')}"
        }

    def ask_general_question(self, prompt):
        """Asks a question to the LLM model and executes functions if necessary."""
        categories = self.get_categories()

        prompt_with_fields = f"""
        {prompt}

        The following parameters can be used to fetch products:
        - 'category' (str): Filter by product category. The available categories are: {', '.join(categories)}.
        - 'price_min' (float): Filter by minimum price of products.
        - 'price_max' (float): Filter by maximum price of products.
        - 'limit' (int, default 10): Number of products to return.
        - 'page' (int, default 1): Page number for pagination.

        Use the format FUNCTION(name, argument) ONLY if you need to execute something to answer the question. Examples:
        FUNCTION(get_products, category='Musical_Instruments', price_min=100, price_max=500, limit=5)
        FUNCTION(get_products, category='Videogames', price_min=100, price_max=500, limit=5)
        """

        payload = {"prompt": prompt_with_fields}

        try:
            print(f"Sending request to {self.api_url} with headers: {self.headers} and payload: {payload}")

            response = requests.post(self.api_url, json=payload, headers=self.headers)
            response.raise_for_status()
            execution_id = response.json().get("id")

            if not execution_id:
                return "No execution ID returned, cannot proceed."

            answer_text = self.get_workflow_result(execution_id)

            return self.execute_function(answer_text)

        except requests.exceptions.RequestException as e:
            return f"Error during request to Eden AI: {e}"

    def get_workflow_result(self, execution_id):
        url = f"{self.api_url}{execution_id}"

        for _ in range(5):
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                result = response.json()
                if result.get("content", {}).get("status") == "succeeded":
                    text_results = result.get("content", {}).get("results", {}).get("text__chat", {}).get("results", [])
                    if text_results:
                        return text_results[0].get("generated_text", "No generated text provided.")

                time.sleep(2)

            except requests.exceptions.RequestException as e:
                return f"Error during request to Eden AI: {e}"

        return "Error: Workflow did not complete in time."

    def ask_based_on_reviews(self, reviews_text, question):
        """
        Asks a generative model using the review text.
        """
        reviews_text_combined = " ".join(reviews_text)  
        prompt = f"I have a user that made me the following question: {question}\n\nGive a brief answer to my user basing on the following reviews. Be clear, concise and respond to the user question:\n{reviews_text_combined}\n\nAdd at the end of your response, check the highlighted reviews for more information on the topic."
        return self.ask_general_question(prompt)

    def get_products(self, category=None, price_min=None, price_max=None, limit=10, page=1):
        """
        Calls the own API to get products based on the given parameters
        like category, minimum price, maximum price, limit, and page.
        """
        try:
            params = {
                "category": category,
                "price_min": price_min,
                "price_max": price_max,
                "limit": limit,
                "page": page
            }

            base_url = request.host_url 
            response = requests.get(f"{base_url}/api/v0/products", params=params, headers=self.headers)
            response.raise_for_status()

            products = response.json().get("products", [])
            if not products:
                return "No products found."

            return products

        except requests.exceptions.RequestException as e:
            return f"Error during product request: {e}"
        
    def get_categories(self):
        """Fetches product categories from the corresponding endpoint."""
        try:
            base_url = request.host_url
            response = requests.get(f"{base_url}/api/v0/products/categories", headers=self.headers)
            response.raise_for_status()

            categories = response.json().get("categories", [])
            if not categories:
                return ["No categories found."]

            return categories

        except requests.exceptions.RequestException as e:
            return [f"Error during category request: {e}"]

    def execute_function(self, answer_text):
        if "FUNCTION(get_products," in answer_text:

            start = answer_text.find("FUNCTION(get_products,") + len("FUNCTION(get_products,")
            end = answer_text.find(")", start)
            params_str = answer_text[start:end].strip()

            parameters = {param.split('=')[0].strip(): param.split('=')[1].strip() for param in params_str.split(',')}
            category = parameters.get('category', None).strip("'")
            price_min = float(parameters.get('price_min', 0)) if 'price_min' in parameters else None
            price_max = float(parameters.get('price_max', 0)) if 'price_max' in parameters else None
            limit = int(parameters.get('limit', 10)) if 'limit' in parameters else 10
            page = int(parameters.get('page', 1)) if 'page' in parameters else 1

            products = self.get_products(category=category, price_min=price_min, price_max=price_max, limit=limit, page=page)
            
            if isinstance(products, list):
                products_text = ", ".join([prod["title"] for prod in products]) 
                return f"Products found: {products_text}"
            else:
                return products 

        return answer_text

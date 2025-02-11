import os
import requests
import time
from dotenv import load_dotenv
from flask import request, jsonify
import json

load_dotenv()

class EdenAIChatService:
    def __init__(self):
        self.api_url = os.getenv("EDEN_API_URL")
        self.headers = {
            "Authorization": f"Bearer {os.getenv('EDEN_API_TOKEN')}",
            "accept": "application/json",
            "content-type": "application/json"
        }

    def ask_general_question_streaming(self, prompt):
        """Sends a request to Eden AI and retrieves the streaming response."""
        url = "https://api.edenai.run/v2/text/chat/stream"  
        payload = {
            "response_as_dict": True,
            "attributes_as_list": False,
            "show_base_64": True,
            "show_original_response": False,
            "temperature": 0,
            "max_tokens": 100,
            "tool_choice": "auto",
            "fallback_type": "continue",
            "providers": ["openai/gpt-4o-mini"],
            "text": prompt,
            "chatbot_global_action": "You are an agent for an online shopping store. ",
            "previous_history": []
        }

        try:
            # Realiza la llamada a la API de Eden AI
            response = requests.post(url, json=payload, headers=self.headers, stream=True)
            response.raise_for_status()

            # Procesa las respuestas streaming
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    try:
                        data = json.loads(line)
                        text = data.get("text")
                        if text:
                            yield text  
                    except Exception as e:
                        print(f"Error procesando línea: {e}")

        except requests.exceptions.RequestException as e:
            yield f"Error during request to Eden AI: {e}"

        except requests.exceptions.RequestException as e:
            yield f"Error during request to Eden AI: {e}"

    def send_request_to_eden_ai(self, prompt):
        """Sends a request to Eden AI and retrieves the response."""
        payload = {"prompt": prompt}
        try:
            response = requests.post(self.api_url, json=payload, headers=self.headers)
            response.raise_for_status()
            execution_id = response.json().get("id")
            
            if not execution_id:
                return {"error": "No execution ID returned, cannot proceed."}
            
            answer_text = self.get_workflow_result(execution_id)
            print(f"Answer text received from EdenAI: {answer_text}")
            return answer_text
        except requests.exceptions.RequestException as e:
            return {"error": f"Error during request to Eden AI: {e}"}
        


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

                time.sleep(5)

            except requests.exceptions.RequestException as e:
                return {"error": f"Error during request to Eden AI: {e}"}

        return {"error": "Error: Workflow did not complete in time."}



    def ask_general_question(self, prompt):
        """Asks a question to the LLM model and executes functions if necessary."""

        categories = self.get_categories()
        prompt_with_fields = f"""The user has entered the following prompt: 

        {prompt}

        If the question requires fetching products, use the 'get_products' function. The products will be shown on screen. Use the following parameters (they are optional, use only those required to answer the user):
        - 'name' (str): Search term for product title. If specified, filters by product name.
        - 'category' (str): Filter by product category. Available categories: {', '.join(categories)}.
        - 'price_min' (float): Minimum price filter.
        - 'price_max' (float): Maximum price filter.
        - 'limit' (int, default 10): Number of products to return.
        - 'page' (int, default 1): Page number for pagination.

        To retrieve products, always use the FUNCTION format as shown below:
        FUNCTION(get_products, name='optional_search_term', category='optional_category', price_min=optional_min_price, price_max=optional_max_price, limit=optional_limit, page=optional_page)
        """

        answer_text = self.send_request_to_eden_ai(prompt_with_fields)

        if isinstance(answer_text, dict) and "error" in answer_text:
            return answer_text
    
        result = self.execute_function(answer_text)

        if isinstance(result, dict) and "products" in result:
            refined_result = self.refine_products_based_on_query(result["products"], prompt)
            
            if isinstance(refined_result, dict) and "error" in refined_result:
                return refined_result

            return refined_result
        return {"answer": result}

        

    def refine_products_based_on_query(self, products, prompt):
        """Envía el JSON de productos de nuevo al chat para refinar la búsqueda y obtener una mejor respuesta."""
        prompt_refinement = f"""
        Here is a list of products:
        {products}

        Based on the user query: "{prompt}", filter and return only the relevant products.
        Additionally, generate a short answer summarizing the best matching products.

        Please return the response in a JSON format with two fields:
        1. 'products' containing the filtered list of products.
        2. 'answer' containing a brief summary of the best matching products.
        """

        print(f"Refining products with the prompt: {prompt_refinement}") 
        
        result = self.send_request_to_eden_ai(prompt_refinement)

        if isinstance(result, dict) and "error" in result:
            print(f"Error during product refinement: {result['error']}")
            return result

        try:
            print(f"Result received from Eden AI: {result}")
            cleaned_result = result.strip('```json').strip('```').strip()

            refined_data = json.loads(cleaned_result)
            return refined_data
        

        except json.JSONDecodeError as e:
            return {"error": f"Error decoding JSON from response: {e}"}
        except Exception as e:
            return {"error": f"Error processing Eden AI response: {e}"}
        



    def ask_based_on_reviews(self, reviews_text, question):
        """
        Asks a generative model using the review text.
        """
        reviews_text_combined = " ".join(reviews_text)  
        prompt = f"I have a user that made me the following question: {question}\n\nGive a brief answer to my user basing on the following reviews. Be clear, concise and respond to the user question:\n{reviews_text_combined}\n\nAdd at the end of your response, check the highlighted reviews for more information on the topic."
                
        answer_text = self.send_request_to_eden_ai(prompt)

        return answer_text

    def get_products(self, name=None, category=None, price_min=None, price_max=None, limit=10, page=1):
        """
        Calls the own API to get products based on the given parameters
        like category, minimum price, maximum price, limit, and page.
        """
        try:
            params = {
                "name": name,
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

            return {"answer": "Products found.", "products": products}

        except requests.exceptions.RequestException as e:
            return {"error": f"Error during product request: {e}"}
        
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
            name = parameters.get('name', None).strip("'") if parameters.get('name') else ''
            category = parameters.get('category', None).strip("'") if parameters.get('category') else ''
            price_min = float(parameters.get('price_min', 0)) if 'price_min' in parameters else None
            price_max = float(parameters.get('price_max', 0)) if 'price_max' in parameters else None
            limit = int(parameters.get('limit', 10)) if 'limit' in parameters else 10
            page = int(parameters.get('page', 1)) if 'page' in parameters else 1

            products_result = self.get_products(name=name, category=category, price_min=price_min, price_max=price_max, limit=limit, page=page)
            
            if isinstance(products_result, dict) and "products" in products_result:
                products = products_result.get("products", [])
                products_text = ", ".join([prod["title"] for prod in products]) 
                return {"response": f"Products found: {products_text}", "products": products}
            else:
                return products_result 

        return answer_text

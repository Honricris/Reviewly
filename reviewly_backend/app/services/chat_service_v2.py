import os
import requests
import json
from dotenv import load_dotenv
from app.services.product_service import get_product_by_id, get_all_categories
from app import create_app
from app.services.customer_function_handlers import CustomerHandlers

load_dotenv()
class ChatService:
    #Cambiar endpoint barra.
    #Mejorar frontend productos y chat y producto especifico


    #One tap google ? 
    #Arreglar remember me. 

    #arreglar go to reviews
    #Elegir modelos gemini 4o mini qwen deepseek 

    #Modificar algoritmo search, para repetir query y modificar busqueda inicial
    # Incluir imagenes de producto?
    def __init__(self, session_id):
        self.session_id = session_id

        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json"
        }
        self.messages = [
            {
                "role": "system",
                "content": "You are an  assistant for an online store. You can answer questions about product information, provide recommendations, and help customers with their purchases. You can not make directly purchases. Never show images in your responses."
            }
        ]
        self.product_id = None 
        

        app = create_app()
        with app.app_context():
            categories = get_all_categories()

    
        if categories:
            categories_str = ", ".join(categories)
            self.messages.append({
                "role": "system",
                "content": f"Available product categories: {categories_str}"
            })

        self.tool_functions = {
            "search_product": CustomerHandlers.handle_search_product,
            "get_reviews_by_embedding":  CustomerHandlers.handle_get_reviews_by_embedding
        }


    def ask_question(self, prompt=None, product_id=None, model="openai/gpt-4o-mini"):
        if prompt:
            self.messages.append({"role": "user", "content": prompt})
        
        if product_id:
            self.product_id = product_id 

            app = create_app()
            with app.app_context():
                product = get_product_by_id(self.product_id)
            
            if product:
                product_str = json.dumps(product) 
                self.messages.append({
                    "role": "system",
                    "content": f"Currently viewing product: {product_str}"
                })

        print(f"Product_id:  {self.product_id}" )

        payload = {
            "model": model,
            "messages": self.messages,
            "top_p": 1,
            "temperature": 0.2,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "repetition_penalty": 1,
            "top_k": 0,
            "stream": True,
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "search_product",
                        "description": "Search for products, games, or  any items on an online store or platform based on a text query provided by the user. This function should be triggered when the user provides a description, keyword, or detail about a product, game, or group of products they are looking for.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "Product name or description."},
                                 "category": {
                                    "type": "string",
                                    "description": "Main category of the product, Optional."
                                },
                                "min_price": {
                                    "type": "number",
                                    "description": "Minimum price filter for the search results. Optional."
                                },
                                "max_price": {
                                    "type": "number",
                                    "description": "Maximum price filter for the search results. Optional."
                                },
                                "top_n": {"type": "integer", "description": "The number of products to return.","default": 5}
                            },
                            "required": ["query"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_reviews_by_embedding",
                        "description": "Retrieve reviews or feedback for products, games, or any items based on a text query provided by the user. This function should be triggered when the user asks for information or reviews related to a specific product, game, or item. The query should be analyzed to identify key details about the product or item, and relevant reviews should be retrieved and presented to the user. Always start the answer with 'Based on the reviews...'",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query_text": {"type": "string", "description": "User query about the product."},
                            },
                            "required": ["query"]
                        }
                    }
                }
            ]
        }
        
        if not product_id:
            payload['tools'][1]['function']['parameters']['properties']['product_name_or_description'] = {
                "type": "string", 
                "description": "Product name or description."
            }
            payload['tools'][1]['function']['parameters']['required'].append('product_name_or_description')


        
        print("Payload enviado a OpenRouter AI:", json.dumps(payload, indent=4))
        
        try:
            print("Enviando solicitud a OpenRouter AI...")
            with requests.post(self.api_url, headers=self.headers, json=payload, stream=True) as response:
                response.raise_for_status()
                response.encoding = 'utf-8'
                
                buffer = ""
                assistant_response = ""
                tool_call_detected = False
                tool_calls_buffer = {}

                for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                    buffer += chunk
                    while True:
                        try:
                            line_end = buffer.find('\n')
                            if line_end == -1:
                                break
                            line = buffer[:line_end].strip()
                            buffer = buffer[line_end + 1:]

                            if line.startswith('data: '):
                                data = line[6:]
                                if data == '[DONE]':
                                    self.messages.append({"role": "assistant", "content": assistant_response})
                                    return
                                try:
                                    data_obj = json.loads(data)
                                    # print(f"Datos decodificados: {data_obj}")

                                    if "choices" in data_obj and data_obj["choices"][0]["delta"].get("tool_calls"):
                                        if not tool_call_detected:
                                            tool_call_detected = True
                                            for tool_call in data_obj["choices"][0]["delta"]["tool_calls"]:
                                                tool_calls_buffer[tool_call["index"]] = {
                                                    "id": tool_call["id"],
                                                    "name": tool_call["function"]["name"],
                                                    "arguments": ""
                                                }
                                            continue  

                                    if tool_call_detected and "choices" in data_obj:
                                        for tool_call in data_obj["choices"][0]["delta"].get("tool_calls", []):
                                            if tool_call["index"] in tool_calls_buffer:
                                                tool_calls_buffer[tool_call["index"]]["arguments"] += tool_call["function"].get("arguments", "")
                                        
                                    if tool_call_detected and data_obj["choices"][0].get("finish_reason") == "tool_calls":

                                        function_name = list(tool_calls_buffer.values())[0]['name']

                                        if function_name == "search_product":
                                            yield json.dumps({"type": "status", "message": "Searching for products"})

                                        elif function_name == "get_reviews_by_embedding":
                                            if self.product_id:
                                                try:
                                                    args = json.loads(list(tool_calls_buffer.values())[0]['arguments'])
                                                    args['product_id'] = self.product_id
                                                    list(tool_calls_buffer.values())[0]['arguments'] = json.dumps(args)
                                                except json.JSONDecodeError:
                                                    print("Error al decodificar argumentos existentes")
                                            
                                            yield json.dumps({"type": "status", "message": "Searching information in the reviews"})
                                        else:
                                            yield json.dumps({"type": "status", "message": f"Executing function {function_name}"})


                                        responses = self._handle_tool_calls(list(tool_calls_buffer.values()))
                                        for response in responses:
                                            self.messages.append({"role": "tool", "name": response["name"], "tool_call_id": response["id"], "content": response["content"]})
                                            if response.get("additional_data"):
                                                yield json.dumps({
                                                    "type": "additional_data",
                                                    "data": response["additional_data"]
                                                })
                                        yield from self.ask_question() 

                                    if "choices" in data_obj and data_obj["choices"][0]["delta"].get("content"):
                                        assistant_response += data_obj["choices"][0]["delta"]["content"]
                                        yield data_obj["choices"][0]["delta"]["content"]

                                except json.JSONDecodeError:
                                    print("Error al decodificar JSON en el streaming")
                        except Exception as e:
                            print("Error en el procesamiento del streaming:", e)
                            break
        except requests.exceptions.RequestException as e:
            print(f"Error durante la solicitud a OpenRouter AI: {e}")
            yield json.dumps({"error": "The service is currently unavailable. Please try again later."})
        except Exception as e:
            print(f"Ocurrió un error inesperado: {e}")
            yield f"Ocurrió un error inesperado: {e}"

    def _handle_tool_calls(self, tool_calls):
        responses = []
        for tool_call in tool_calls:
            function_name = tool_call["name"]
            if function_name in self.tool_functions:
                try:
                    args = json.loads(tool_call["arguments"])
                    print(f"Argumentos recibidos para {function_name}: {args}")

                    self.messages.append({
                    "role": "assistant",
                    "content": None, 
                    "tool_calls": [
                        {
                            "id": tool_call["id"],  
                            "type": "function", 
                            "function": {
                                "name": function_name, 
                                "arguments": json.dumps(args)  
                            }
                        }
                    ]
                })
                    

                    response = self.tool_functions[function_name](args)
                    response_data = json.loads(response)
                    responses.append({
                        "id": tool_call["id"],
                        "name": function_name,
                        "content":  response_data["response_text"],
                        "additional_data": response_data.get("additional_data", {})  

                    })
                except json.JSONDecodeError:
                    print(f"Error al decodificar argumentos para {function_name}: {tool_call['arguments']}")
        return responses

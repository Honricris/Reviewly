import os
import requests
import json
from dotenv import load_dotenv
from app.services.product_service import get_product_by_id, get_all_categories
from app.services.user_service import UserService
from app import create_app
from app.services.customer_function_handlers import CustomerHandlers
from app.services.admin_function_handlers import AdminHandlers

load_dotenv()
class ChatService:
    _instances = {}

    @classmethod
    def get_instance(cls, user_id):
        if user_id not in cls._instances:
            cls._instances[user_id] = cls(user_id)
        return cls._instances[user_id]

    @classmethod
    def remove_instance(cls, user_id):
        if user_id in cls._instances:
            del cls._instances[user_id]
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        # Determine if user is admin
        app = create_app()
        with app.app_context():
            user = UserService.get_user_by_id(user_id)
            self.is_admin = user.role.lower() == "admin" if user else False

        # Set base system message based on role
        if self.is_admin:
            self.messages = [{
                "role": "system",
                "content": "You are an admin assistant for an online store. You have access to both customer-facing features and administrative functions. You can manage user information, answer questions about products, provide recommendations, and assist with store operations. Never show images in your responses."
            }]
        else:
            self.messages = [{
                "role": "system",
                "content": "You are an assistant for an online store. You can answer questions about product information, provide recommendations, and help customers with their purchases. You cannot make direct purchases. Never show images in your responses."
            }]
            
        self.product_id = None 

        # Add categories info
        with app.app_context():
            categories = get_all_categories()
        if categories:
            categories_str = ", ".join(categories)
            self.messages.append({
                "role": "system",
                "content": f"Available product categories: {categories_str}"
            })

        # Define tool functions based on user role
        self.tool_functions = {
            "search_product": CustomerHandlers.handle_search_product,
            "get_reviews_by_embedding": CustomerHandlers.handle_get_reviews_by_embedding
        }
        if self.is_admin:
            self.tool_functions.update({
                "get_users": AdminHandlers.handle_get_users,
                "get_user_by_id": AdminHandlers.handle_get_user_by_id,
                "set_user_role": AdminHandlers.handle_set_user_role

            })

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

        # Base tools available to all users
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_product",
                    "description": "Search for products, games, or any items on an online store or platform based on a text query provided by the user.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Product name or description."},
                            "category": {"type": "string", "description": "Main category of the product, Optional."},
                            "min_price": {"type": "number", "description": "Minimum price filter for the search results. Optional."},
                            "max_price": {"type": "number", "description": "Maximum price filter for the search results. Optional."},
                            "top_n": {"type": "integer", "description": "The number of products to return.", "default": 5}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_reviews_by_embedding",
                    "description": "Retrieve reviews or feedback for products based on a text query. Always start the answer with 'Based on the reviews...'",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query_text": {"type": "string", "description": "User query about the product."},
                        },
                        "required": ["query_text"]
                    }
                }
            }
        ]

        # Add admin-specific tools
        if self.is_admin:
            tools.extend([
                {
                    "type": "function",
                    "function": {
                        "name": "get_users",
                        "description": "Retrieve a list of users with optional filters (admin only)",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "limit": {"type": "integer", "description": "Maximum number of users to return", "default": 5},
                                "email": {"type": "string", "description": "Exact email match (optional)"},
                                "email_starts_with": {"type": "string", "description": "Filter emails starting with this string (optional)"},
                                "role": {"type": "string", "description": "Filter by role (must be 'user' or 'admin')", "enum": ["user", "admin"]},
                                "github_id": {"type": "integer", "description": "Exact GitHub ID match (optional)"},
                                "has_github_id": {"type": "boolean", "description": "Filter users with/without GitHub ID (optional)"}
                            },
                            "required": []
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "get_user_by_id",
                        "description": "Retrieve a specific user by their ID (admin only)",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "integer", "description": "The ID of the user to retrieve"}
                            },
                            "required": ["user_id"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "set_user_role",
                        "description": "Change a user's role (admin only)",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "integer", "description": "The ID of the user to modify"},
                                "new_role": {"type": "string", "description": "The new role to assign", "enum": ["user", "admin"]}
                            },
                            "required": ["user_id", "new_role"]
                        }
                    }
                }
            ])

        # Adjust get_reviews_by_embedding parameters based on product_id
        if not product_id:
            tools[1]["function"]["parameters"]["properties"]["product_name_or_description"] = {
                "type": "string",
                "description": "Product name or description."
            }
            tools[1]["function"]["parameters"]["required"].append("product_name_or_description")

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
            "tools": tools
        }

        try:
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
                                        status_messages = {
                                            "search_product": "Searching for products",
                                            "get_reviews_by_embedding": "Searching information in the reviews",
                                            "get_users": "Retrieving user list",
                                            "get_user_by_id": "Retrieving user information",
                                            "set_user_role": "Updating user role"
                                        }
                                        yield json.dumps({
                                            "type": "status",
                                            "message": status_messages.get(function_name, f"Executing function {function_name}")
                                        })

                                        if function_name == "get_reviews_by_embedding" and self.product_id:
                                            try:
                                                args = json.loads(list(tool_calls_buffer.values())[0]['arguments'])
                                                args['product_id'] = self.product_id
                                                list(tool_calls_buffer.values())[0]['arguments'] = json.dumps(args)
                                            except json.JSONDecodeError:
                                                print("Error al decodificar argumentos existentes")

                                        responses = self._handle_tool_calls(list(tool_calls_buffer.values()))
                                        for response in responses:
                                            self.messages.append({
                                                "role": "tool",
                                                "name": response["name"],
                                                "tool_call_id": response["id"],
                                                "content": response["content"]
                                            })
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
            yield json.dumps({"error": "The service is currently unavailable. Please try again later."})
        except Exception as e:
            yield f"Ocurrió un error inesperado: {e}"

    def _handle_tool_calls(self, tool_calls):
        responses = []
        for tool_call in tool_calls:
            function_name = tool_call["name"]
            if function_name in self.tool_functions:
                try:
                    args = json.loads(tool_call["arguments"])
                    self.messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [{
                            "id": tool_call["id"],
                            "type": "function",
                            "function": {
                                "name": function_name,
                                "arguments": json.dumps(args)
                            }
                        }]
                    })
                    response = self.tool_functions[function_name](args)
                    response_data = json.loads(response)
                    responses.append({
                        "id": tool_call["id"],
                        "name": function_name,
                        "content": response_data["response_text"],
                        "additional_data": response_data.get("additional_data", {})
                    })
                except json.JSONDecodeError:
                    print(f"Error al decodificar argumentos para {function_name}: {tool_call['arguments']}")
        return responses
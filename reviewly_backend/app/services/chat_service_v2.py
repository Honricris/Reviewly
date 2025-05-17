import os
import requests
import json
from dotenv import load_dotenv
from app.services.product_service import get_product_by_id, get_all_categories
from app.services.user_service import UserService
from app import create_app
from app.services.customer_function_handlers import CustomerHandlers
from app.services.admin_function_handlers import AdminHandlers
from datetime import datetime

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
        
        app = create_app()
        with app.app_context():
            user = UserService.get_user_by_id(user_id)
            self.is_admin = user.role.lower() == "admin" if user else False

        current_date = datetime.now().strftime("%B %d, %Y")
        
        if self.is_admin:
            self.messages = [{
                "role": "system",
                "content": f"You are an admin assistant for an online store. Today's date is {current_date}. You can manage user information, generate reports, answer questions about products, provide recommendations, assist with store operations, and generate charts for data visualization. Never show images in your responses.  Do not call get_users, generate_user_activity_report, or generate_product_popularity_report directly to obtain data for charts since they only MUST be used to generate when the user asks for a report."
            }]
        else:
            self.messages = [{
                "role": "system",
                "content": f"You are an assistant for an online store. Today's date is {current_date}. You can answer questions about product information, provide recommendations, and help customers with their purchases. You cannot make direct purchases. Never show images in your responses."
            }]
            
        self.product_id = None 

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
            "get_reviews_by_embedding": CustomerHandlers.handle_get_reviews_by_embedding
        }
        if self.is_admin:
            self.tool_functions.update({
                "get_users": AdminHandlers.handle_get_users,
                "get_user_by_id": AdminHandlers.handle_get_user_by_id,
                "set_user_role": AdminHandlers.handle_set_user_role,
                "delete_user": AdminHandlers.handle_delete_user,
                "generate_user_activity_report": AdminHandlers.handle_generate_user_activity_report,
                "generate_product_popularity_report": AdminHandlers.handle_generate_product_popularity_report,
                "generate_chart": AdminHandlers.handle_generate_chart
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
                                "email_contains": {"type": "string", "description": "Filter emails containing this string (optional)"},
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
                },
                {
                    "type": "function",
                    "function": {
                        "name": "delete_user",
                        "description": "Delete a user from the system (admin only)",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "user_id": {"type": "integer", "description": "The ID of the user to delete"}
                            },
                            "required": ["user_id"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "generate_user_activity_report",
                        "description": "Generate a user activity report with optional date range and role filters (admin only). Do not call this function to generate data for charts since it does not return data it only creates a pdf in the user end",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "start_date": {"type": "string", "description": "Start date for login activity (YYYY-MM-DD), optional"},
                                "end_date": {"type": "string", "description": "End date for login activity (YYYY-MM-DD), optional"},
                                "role": {"type": "string", "description": "Filter by user role (All, user, or admin), optional", "enum": ["All", "user", "admin"]}
                            },
                            "required": []
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "generate_product_popularity_report",
                        "description": "Generate a product popularity report with optional filters (admin only). Do not call this function to generate data for charts since it does not return data it only creates a pdf in the user end",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "category": {"type": "string", "description": "Filter by product category, optional"},
                                "min_price": {"type": "number", "description": "Minimum price filter, optional"},
                                "max_price": {"type": "number", "description": "Maximum price filter, optional"},
                                "min_rating": {"type": "number", "description": "Minimum average rating filter (0-5), optional"},
                                "min_favorites": {"type": "number", "description": "Minimum number of favorites filter, optional"},
                                "sort_by": {"type": "string", "description": "Sort results by field", "enum": ["title", "price", "favorites", "rating", "reviews"]},
                                "sort_order": {"type": "string", "description": "Sort order (ascending or descending). Use it in combination with the sort_by property to sort by ascending or descending order", "enum": ["asc", "desc"], "default": "asc"}
                            },
                            "required": []
                        }
                    }
                },
              {
                "type": "function",
                "function": {
                    "name": "generate_chart",
                    "description": "Generate a Chart.js chart for data visualization (admin only). Requires pre-aggregated data (labels and values) from previous function calls (e.g., get_users or search_product). The chatbot must process the data into the required format before calling this function. Do not call get_users, generate_user_activity_report, or generate_product_popularity_report directly to obtain data.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "chart_type": {
                                "type": "string",
                                "description": "Type of chart to generate",
                                "enum": ["bar", "line", "pie", "doughnut"]
                            },
                            "data_source": {
                                "type": "string",
                                "description": "Source of the data (e.g., 'users', 'products')",
                                "enum": ["users", "products"]
                            },
                            "x_axis": {
                                "type": "string",
                                "description": "Field for x-axis or labels (e.g., 'role', 'category'). For pie/doughnut charts, this represents the label field."
                            },
                            "y_axis": {
                                "type": "string",
                                "description": "Field for y-axis or values (e.g., 'count', 'price'). For pie/doughnut charts, this represents the value field."
                            },
                            "title": {
                                "type": "string",
                                "description": "Title of the chart"
                            },
                            "data": {
                                "type": "object",
                                "description": "Pre-aggregated data for the chart, containing labels and values",
                                "properties": {
                                    "labels": {
                                        "type": "array",
                                        "description": "Array of labels for the chart (e.g., ['user', 'admin'] for user roles)",
                                        "items": {"type": "string"}
                                    },
                                    "values": {
                                        "type": "array",
                                        "description": "Array of values corresponding to the labels (e.g., [3, 2] for user/admin counts)",
                                        "items": {"type": "number"}
                                    }
                                },
                                "required": ["labels", "values"]
                            }
                        },
                        "required": ["chart_type", "data_source", "x_axis", "y_axis", "title", "data"]
                    }
                }
            }
            ])

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
                                            "set_user_role": "Updating user role",
                                            "delete_user": "Deleting user",
                                            "generate_user_activity_report": "Generating user activity report",
                                            "generate_product_popularity_report": "Generating product popularity report",
                                            "generate_chart": "Generating chart data"
                                        }
                                        status_msg = status_messages.get(function_name, f"Executing function {function_name}")
                                        yield json.dumps({
                                            "type": "status",
                                            "message": status_msg
                                        })

                                        if function_name == "get_reviews_by_embedding" and self.product_id:
                                            try:
                                                args = json.loads(list(tool_calls_buffer.values())[0]['arguments'])
                                                args['product_id'] = self.product_id
                                                list(tool_calls_buffer.values())[0]['arguments'] = json.dumps(args)
                                            except json.JSONDecodeError:
                                                pass

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
                                    pass
                        except Exception as e:
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
                    
                    response_dict = {
                        "id": tool_call["id"],
                        "name": function_name,
                        "content": response_data["response_text"],
                        "additional_data": response_data.get("additional_data", {})
                    }
                    responses.append(response_dict)
                except json.JSONDecodeError:
                    pass
        return responses
import os
import requests
import json
from dotenv import load_dotenv
from app.services.product_service import searchProduct
from app import create_app

load_dotenv()

class ChatService:
    def __init__(self):
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json"
        }
        self.messages = [
            {
                "role": "system",
                "content": "You are an assistant for an online store. You can answer questions about product information, provide recommendations, and help customers with their purchases."
            }
        ]
        
        self.tool_functions = {
            "search_product": self._handle_search_product
        }

    def ask_question(self, prompt=None, product_id=None):
        if prompt:
            self.messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": "openai/gpt-4o-mini",
            "messages": self.messages,
            "top_p": 1,
            "temperature": 0.2,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "repetition_penalty": 1,
            "top_k": 0,
            "stream": True,
            "tools": [{
                "type": "function",
                "function": {
                    "name": "search_product",
                    "description": "Search for products based on a text query. Use it if the user asks for searching a product or products.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The name or description of the product."
                            },
                            "top_n": {
                                "type": "integer",
                                "description": "The number of products to return.",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                }
            }]
        }
        
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
                                    
                                    # Detectar el primer tool_call solo una vez
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

                                    # Si ya se detectó un tool_call, acumulamos sus argumentos
                                    if tool_call_detected and "choices" in data_obj:
                                        for tool_call in data_obj["choices"][0]["delta"].get("tool_calls", []):
                                            if tool_call["index"] in tool_calls_buffer:
                                                tool_calls_buffer[tool_call["index"]]["arguments"] += tool_call["function"].get("arguments", "")
                                        
                                    # Cuando termina la tool_call, procesamos los datos
                                    if tool_call_detected and data_obj["choices"][0].get("finish_reason") == "tool_calls":
                                        responses = self._handle_tool_calls(list(tool_calls_buffer.values()))
                                        for response in responses:
                                            self.messages.append({"role": "tool", "name": response["name"], "tool_call_id": response["id"], "content": response["content"]})
                                        yield from self.ask_question() 

                                    # Procesamiento normal de respuestas de texto
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
            yield f"Error durante solicitud a OpenRouter AI: {e}"
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
                    responses.append({
                        "id": tool_call["id"],
                        "name": function_name,
                        "content": response
                    })
                except json.JSONDecodeError:
                    print(f"Error al decodificar argumentos para {function_name}: {tool_call['arguments']}")
        return responses

    def _handle_search_product(self, args):
        query = args["query"]
        top_n = args.get("top_n", 5)
        app = create_app()
        with app.app_context():
            response = searchProduct(query, top_n)
        
        response.pop('query', None)
        
        for product in response.get('top_products', []):
            product.pop('images', None)
            product.pop('product_id', None)
        
        return json.dumps(response)

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class ChatService:
    def __init__(self):
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json"
        }
        self.messages = [] 

    def ask_general_question(self, prompt):
        """Sends a streaming request to OpenRouter AI and retrieves the response."""
        self.messages.append({"role": "user", "content": prompt})

        payload = {
            "model": "google/gemini-2.0-pro-exp-02-05:free",
            "messages": self.messages,  
            "top_p": 1,
            "temperature": 0.2,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "repetition_penalty": 1,
            "top_k": 0,
            "stream": True
        }

        try:
            print("Enviando solicitud a OpenRouter AI...")
            with requests.post(self.api_url, headers=self.headers, json=payload, stream=True) as response:
                response.raise_for_status()
                print("\nPayload enviado:")
                print(json.dumps(payload, indent=4)) 
                print("\nRespuesta completa del servicio:")
                print(response.text) 
                
                print("\nTexto en streaming:")
                buffer = ""
                response_content = ""  
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
                                    if response_content:
                                        self.messages.append({"role": "assistant", "content": response_content})
                                    return response_content  
                                try:
                                    data_obj = json.loads(data)
                                    content = data_obj["choices"][0]["delta"].get("content")
                                    if content:
                                        response_content += content  
                                        print(content, end="", flush=True)
                                except json.JSONDecodeError:
                                    pass
                        except Exception:
                            break
        except requests.exceptions.RequestException as e:
            print(f"Error durante la solicitud a OpenRouter AI: {e}")
        except Exception as e:
            print(f"Ocurrió un error inesperado: {e}")


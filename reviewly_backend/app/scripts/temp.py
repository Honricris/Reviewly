import requests
import json
import random

class EdenAI:
    def __init__(self):
        self.api_url = "https://api.edenai.run/v2/text/chat"
        self.headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMzBmNWQzOGMtZjJjNS00MWQ2LTk3N2QtMmMwMTAxNDYxNWQzIiwidHlwZSI6ImFwaV90b2tlbiJ9.AWQeXGCaK1kvAZa60YHSqr_3AB1qWcDSW_vMiDkNFgU"
        }  # Cambia esto por tu clave de API

    def ask_general_question_streaming(self, prompt):
        """Envía una solicitud a Eden AI y obtiene la respuesta en streaming."""
        payload = {
            "response_as_dict": True,
            "attributes_as_list": False,
            "show_base_64": True,
            "show_original_response": False,
            "temperature": 0,
            "max_tokens": 100,
            "tool_choice": "auto",
            "fallback_type": "rerun",
            "providers": ["openai/gpt-4o-mini"],
            "text": prompt,
            "chatbot_global_action": "Include your chain of thought in the response, as well as the tools you have used",
            "previous_history": [],
            "available_tools": [
                {
                    "name": "get_joke",
                    "description": "Tells a random joke to the user.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            ]
        }

     
        print("Enviando solicitud a Eden AI...")
        response = requests.post(self.api_url, json=payload, headers=self.headers, stream=True)
        response.raise_for_status()
        print("Respuesta recibida correctamente.")
        print("Respuesta del asistente:", response.json())


    def get_joke(self):
        """Simula contar un chiste aleatorio."""
        jokes = [
            "¿Por qué los pájaros no usan Facebook? Porque ya tienen Twitter.",
            "¿Cómo organizas una fiesta en el espacio? ¡Simple, planeas-netas!",
            "¿Cuál es el café más peligroso del mundo? ¡El ex-preso!",
            "¿Qué le dijo una impresora a otra? ¿Esa hoja es tuya o es una impresión mía?"
        ]
        return random.choice(jokes)

def main():
    eden_ai = EdenAI()
    
    prompt = input("Introduce tu pregunta para Eden AI: ")

    print("\nRespondiendo con Eden AI...")
    full_response = eden_ai.ask_general_question_streaming(prompt)
    print("\nRespuesta completa de Eden AI:")
    print(full_response)  

if __name__ == "__main__":
    main()

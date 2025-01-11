import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

class EdenAIChatService:
    def __init__(self):
        self.api_url = os.getenv("EDEN_API_URL")
        self.headers = {
            "Authorization": f"Bearer {os.getenv('EDEN_API_TOKEN')}"
        }

    def ask_general_question(self, prompt):
        payload = {
            "prompt": prompt
        }

        try:

            print(f"Sending request to {self.api_url} with headers: {self.headers} and payload: {payload}")

            response = requests.post(self.api_url, json=payload, headers=self.headers)

            response.raise_for_status()  
            execution_id = response.json().get("id")

            if not execution_id:
                return "No execution ID returned, cannot proceed."

            return self.get_workflow_result(execution_id)

        except requests.exceptions.RequestException as e:
            return f"Error during request to Eden AI: {e}"

    def get_workflow_result(self, execution_id):
        # Enviar solicitud GET para obtener el resultado del workflow
        url = f"{self.api_url}{execution_id}"

        for _ in range(5):
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                result = response.json()
               # Verificar si el resultado está listo
                if result.get("content", {}).get("status") == "succeeded":
                    # Acceder al texto 
                    text_results = result.get("content", {}).get("results", {}).get("text__chat", {}).get("results", [])
                    if text_results:
                        return text_results[0].get("generated_text", "No generated text provided.")


                time.sleep(2)

            except requests.exceptions.RequestException as e:

                return f"Error during request to Eden AI: {e}"

        return "Error: Workflow did not complete in time."


    def ask_based_on_reviews(self, reviews_text, question):
        """
        Hace una consulta al modelo generativo usando el texto de las reseñas.
        """
        reviews_text_combined = " ".join(reviews_text)  
        prompt = f"I have a user that made me the following question: {question}\n\nGive a brief answer to my user basing on the following reviews. Be clear, concise and respond to the user question:\n{reviews_text_combined}\n\nAdd at the  end of your response, check the higlighted reviews for more information on the topic."
        return self.ask_general_question(prompt)
import cohere
from config.config import COHERE_API_KEY

class LLMHandler:
    def __init__(self):
        self.client = cohere.Client(COHERE_API_KEY)

    def get_response(self, prompt):
        try:
            response = self.client.chat(
                message=prompt,
                model="command",  # Cohere's most capable model
                temperature=0.7
            )
            return response.text
        except Exception as e:
            return f"Error processing request: {str(e)}"
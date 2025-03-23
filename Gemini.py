from google import genai
from google.genai import types
import os

class Geminibot:
    def __init__(self, role):
        self.client = genai.Client(api_key=os.getenv("GEMINI_KEY"))
        self.create_new_chat(role)

    def create_new_chat(self, role):
        self.chat = self.client.chats.create(
            model="gemini-2.0-flash", 
            config=types.GenerateContentConfig(system_instruction=role)
            )

from google import genai
from google.genai import types
import os
import re
import json
from constants import *

class GeminiBot:
    def __init__(self, role):
        self.client = genai.Client(api_key=os.getenv("GEMINI_KEY"))
        if not role=="test_case_generator":
            self.create_new_chat(role)

    def create_new_chat(self, role):
        config = types.GenerateContentConfig(system_instruction=role, tools=FUNCTIONS, max_output_tokens=600)# if role == "test_assitant" else types.GenerateContentConfig(system_instruction=role, max_output_tokens=200)
        
        print(config.tools)
        self.chat = self.client.chats.create(
            model="gemini-2.0-flash", 
            config= config
            )
    
    def generate_testcase(self, Scenario):
        response = self.client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(system_instruction=TESTCASE_INSTRUCTIONS),
        contents=[Scenario]
        )
        op = re.sub("```json","",response.text)
        op = re.sub("```","",op)

        print(op)

    
        return json.loads(op)

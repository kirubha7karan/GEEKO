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
        '''
        Create a new chat session with the specified role.
        '''
        #tool call will be enabled only when not in Rag mode
        config = types.GenerateContentConfig(system_instruction=role, tools=FUNCTIONS) if not "test cases" in role else types.GenerateContentConfig(system_instruction=role)
        self.chat = self.client.chats.create(
            model="gemini-2.0-flash", 
            config= config
            )
    
    def generate_testcase(self, Scenario):
        '''
        Generate test cases based on the provided scenario.
        '''
        
        #Agent for generating test cases
        response = self.client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(system_instruction=TESTCASE_INSTRUCTIONS),
        contents=[Scenario]
        )
        op = re.sub("```json","",response.text)
        op = re.sub("```","",op)

        #followp up question to user for acknowledgement
        response = "**REPHRASE THE TESTCASES IN JSON FORMAT AND ASK ME TO REVIEW THEM** \n"+str(op)+" Do not blindly ask me whether to create them without sending it in you response"
        return response
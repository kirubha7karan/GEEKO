import re
import requests
from types import SimpleNamespace

LLM_URL = "http://localhost:11434/api/chat"

class OllamaBot:
    
    def __init__(self, role):  
        self.data={} 
        self.create_new_chat(role)
        self.chat = self.Chat(self)

    def create_new_chat(self, role):
        self.data = {
        "model": "phi3:latest",
        "messages": [
          {"role": "system", "content": role}
        ],
        "stream": False
      }
        print(self.data)
    
    class Chat:
        def __init__(self, outer_instance):
            self.outer_instance = outer_instance

        def send_message(self,user_text):
            self.outer_instance.data["messages"].append({"role":"user", "content": user_text})
            response = requests.post(LLM_URL, json=self.outer_instance.data)
            response = response.json()["message"]["content"]
            # response = re.sub(r"<think>.*?</think>","",response, flags=re.DOTALL).strip()
            self.outer_instance.data["messages"].append({"role":"assitant", "content": response})
            response = {"text":response} 
            print(self.outer_instance.data)
            return SimpleNamespace(**response)
import os
from google import genai
from google.genai import types

sys_ins = "Your name is Geeko. A Humorous person. You help people with python coding related question alone. For any questions that is other than python\
you make a unrealted joke"
client = genai.Client(api_key=os.getenv("GEMINI_KEY"))


response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="How to print hello world ?",
    config=types.GenerateContentConfig(
        system_instruction=sys_ins)
)

print(response.text)

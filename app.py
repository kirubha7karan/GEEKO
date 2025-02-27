from flask import Flask, render_template, request
import os
from google import genai
from google.genai import types

sys_ins = "Your name is Geeko. You help people with coding related question and general greetings alone.\
For any questions that is other than them you make a unrealted comment. Your maximim response length is 50 characters."

client = genai.Client(api_key=os.getenv("GEMINI_KEY"))

app = Flask(__name__)

@app.route('/',methods=["GET","POST"])
def chat():
    if request.method == "GET":
        return render_template('chatbot.html', response="")
    else:
        user_input = request.form.get('message')
        print("post request received")

        print (user_input)
        if user_input:
            response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=user_input,
            config=types.GenerateContentConfig(
                system_instruction=sys_ins
            )
            )
            response_text = response.text
        else:
            response_text = "No input provided."

        return render_template('chatbot.html', response=response_text)
    
app.run(debug=True)  # Start the server
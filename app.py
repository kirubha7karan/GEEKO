from flask import Flask, jsonify, render_template, request
import os
from google import genai
from google.genai import types

sys_ins = "Your name is Geeko. You help people with coding related question and general greetings alone.\
Your maximim response length is 50 characters."

client = genai.Client(api_key=os.getenv("GEMINI_KEY"))
chat = client.chats.create(
        model="gemini-2.0-flash", 
        config=types.GenerateContentConfig(system_instruction=sys_ins)
        )

app = Flask(__name__)

@app.route('/',methods=["GET","POST"])
def Chat():
    if request.method == "GET":
        return render_template('chatbot.html', response="")
    else:
        user_input = request.json["message"]

        if user_input:
            response = chat.send_message(user_input)
            ''' response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=user_input,
            config=types.GenerateContentConfig(
                system_instruction=sys_ins
            )
            )'''
            response_text = response.text
        else:
            response_text = "No input provided."

        return jsonify({"response": response_text})
    
app.run(debug=True)  # Start the server
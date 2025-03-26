from flask import Flask, jsonify, render_template, request, session
import numpy as np
import json
import io
import random
import string
from Gemini import GeminiBot
from Ollama import OllamaBot
from Helper import *
from Helper import test_cases, faiss_index
from constants import *

global role, chat, test_assitant, bot
role = "bot"
users = {}

app = Flask(__name__)
app.secret_key = 'geekoStar'

@app.route('/',methods=["GET","POST"])
def Chat():
    global role, test_assitant, bot
    if request.method == "GET":
        if not session:
            user = ''.join(random.choices(string.ascii_letters,k=10))
            session["user"] = user
            users[user] =  GeminiBot(role)
        return render_template('chatbot.html', response="")
    
    else:
        response_text =""
        user_input = request.json["message"]
        
        if len(user_input) >200:
            return jsonify({"response": "Max Input Character is 200"}), 400
        
        test_assist = request.json["testAssistance"]
        user = session["user"] 
        if test_assist and role != "test_assitant":
            role = "test_assitant"
            users[user].create_new_chat(TEST_ASSISTANT)
        elif not test_assist and role != "bot":
            role = "bot"
            users[user].create_new_chat(BOT)
            
        if user_input:
            if request.json["testAssistance"]:                 
                
                query_embedding = embedding_model.encode([user_input])
                
                try:
                    faiss_index, test_cases = get_data()
                    D, I = faiss_index.search(np.array(query_embedding), k=5)
                    results = test_cases.iloc[I[0]][["externalid", "summary", "preconditions", "combined_text"]].to_dict(orient="records")
                    user_txt = json.dumps({"query": user_input, "results": results})
                    response = users[user].chat.send_message(user_txt)
                    handle_function_call(response)
                    response_text = response.text
                except:
                    response_text = "Please add a Valid XML file and continue"
                
            else:
                response = users[user].chat.send_message(user_input)
                text = handle_function_call(response)
                if text:
                    response = text
                response_text = response.text
                
        else:
            response_text = "No input provided."

        return jsonify({"response": response_text})

@app.route('/file', methods=["POST"])
def handle_file_upload():
    data = request.json
    if data and 'file' in data:
        xml_content = data['file']  # Raw CSV string

        xml_content = io.StringIO(data['file'])
        try:
            xml_to_csv(xml_content, "./static/knowledge_base.csv")
            var = set_up_knowledge_base()
            
            if var:
                return jsonify({"response": "File uploaded successfully."})
            else:
                return jsonify({"response": "Mandatory fields are missing. Please import testlink exported XML file."}), 400
        except:
            return jsonify({"response": "Mandatory fields are missing. Please import testlink exported XML file."}), 400

    else:
        return jsonify({"response": "File upload failed."}), 400

app.run(debug=True)  # Start the server
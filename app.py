from flask import Flask, jsonify, render_template, request
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from google import genai
from google.genai import types
import pandas as pd
import faiss
import json


# sys_ins = "Your name is Geeko. You are a polite and helpful assistant.\
# Keep responses concise, under 50 characters."

global role, chat, test_assitant, bot
role = "bot"
chat = None
faiss_index =""
test_cases = ""
client = genai.Client(api_key=os.getenv("GEMINI_KEY"))

test_assitant = "# Geeko 2.0 - System Instruction\
You are **Geeko 2.0**, a helpful testing assistant responsible for test cases of the *Armor* application.\
## Behavior Guidelines\
- Respond politely to general greetings.  \
- Maintain professionalism and clarity in responses.  \
- Only discuss *autocomplete* and *geocoding* test cases.\
\
## Response Rules\
1. **If a user asks what you can do**, reply:  \
   *\"I can help you with understanding testcases you have upload.\"*  \
2. **When given a query**, review the provided *TestLink* test cases (`results`) and respond based on the most relevant ones.  \
3. **Do not mention test case IDs** unless explicitly requested by the user.  \
4. **If the user provides a specific test case ID** and asks for an explanation, explain *only that test case*."

bot = "# Geeko 2.0 - System Instruction\
You are **Geeko 2.0**, a helpful assitant\
## Behavior Guidelines\
- Respond politely to general greetings.  \
- Maintain professionalism and clarity in responses."

def create_new_chat(role):
    global chat
    chat = client.chats.create(
        model="gemini-2.0-flash", 
        config=types.GenerateContentConfig(system_instruction=role)
        )

# Load Embedding Model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Load and Process Test Cases from TestLink CSV
def load_test_cases(csv_file):
    df = pd.read_csv(csv_file)

    mandatory_fields = ["externalid", "summary", "preconditions"]
    for field in mandatory_fields:
        if field not in df.columns:
            raise ValueError(f"Mandatory field {field} is missing in the CSV file.")
        
    # Combine all steps and expected results into a single text field
    def combine_steps(row):
        steps_text = []
        for i in range(11):  # Assuming max 11 steps (steps/step/0 to steps/step/10)
            action_col = f"steps/step/{i}/actions"
            expected_col = f"steps/step/{i}/expectedresults"
            
            if action_col in row and expected_col in row:
                action = str(row[action_col]) if pd.notna(row[action_col]) else ""
                expected = str(row[expected_col]) if pd.notna(row[expected_col]) else ""
                steps_text.append(f"Step {i+1}: {action} -> Expected: {expected}")
        
        return " \n ".join(steps_text)    
    df["combined_text"] = df["externalid"].astype(str) + " " + df["summary"] + " " + df["preconditions"] + " " + df.apply(combine_steps, axis=1)
    return df

def embed_texts(texts):
    return np.array(embedding_model.encode(texts))
    
# Initialize FAISS Index
def create_faiss_index(embeddings):
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return index
    
    
def set_up_knowledge_base():
    global faiss_index, test_cases
    # Load and Process Test Cases
    try:
        test_cases = load_test_cases("./static/knowledge_base.csv")
        embeddings = embed_texts(test_cases["combined_text"].tolist())
        faiss_index = create_faiss_index(embeddings)
    except:
        return False
    return True

app = Flask(__name__)


@app.route('/',methods=["GET","POST"])
def Chat():
    global role, chat, test_assitant, bot, faiss_index, test_cases
    if request.method == "GET":
        return render_template('chatbot.html', response="")
    else:
        response_text =""
        user_input = request.json["message"]
        test_assist = request.json["testAssistance"]
        
        if test_assist and role != "test_assitant":
            role = "test_assitant"
            create_new_chat(test_assitant)
        elif not test_assist and role != "bot":
            role = "bot"
            create_new_chat(bot)
            
        if user_input:
            if request.json["testAssistance"]:                 
                
                query_embedding = embedding_model.encode([user_input])
                try:
                    D, I = faiss_index.search(np.array(query_embedding), k=5)
                    results = test_cases.iloc[I[0]][["externalid", "summary", "preconditions", "combined_text"]].to_dict(orient="records")
                    user_txt = json.dumps({"query": user_input, "results": results})
                    response = chat.send_message(user_txt)
                    response_text = response.text
                except:
                    response_text = "Please add a Valid CSV file and continue"
                
            else:
                response = chat.send_message(user_input)
                response_text = response.text
                
        else:
            response_text = "No input provided."

        return jsonify({"response": response_text})

@app.route('/file', methods=["POST"])
def handle_file_upload():
    data = request.json
    if data and 'file' in data:
        csv_content = data['file']  # Raw CSV string

        # Save the raw CSV content to a file
        with open("./static/knowledge_base.csv", "w") as f:
            f.write(csv_content)

        print("File saved")
        var = set_up_knowledge_base()
        
        if var:
            return jsonify({"response": "File uploaded successfully."})
        else:
            print("Failed")
            return jsonify({"response": "Mandatory fields are missing. Please import testlink exported csv"})
    else:
        return jsonify({"response": "File upload failed."}), 400

create_new_chat(role)
app.run(debug=True)  # Start the server
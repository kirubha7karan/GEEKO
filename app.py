from flask import Flask, jsonify, render_template, request, session
import json
import io
import random
import string
from Gemini import *
from dotenv import load_dotenv
# from Ollama import OllamaBot #Uncomment if using Local LLM 

load_dotenv()
global role, chat, test_assitant, bot
role = "bot"
users = {}

app = Flask(__name__)
app.secret_key = 'geekoStar'
vector_DB = Weaviate()
 
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
        
        try:
            user = session["user"] 
        
            #Handling role change in user request
            role = handle_role_change(role, test_assist,user = users[user])
        except Exception as e:
            session.clear()
            '''
            Creating new seesion in case old is expired
            '''
            print("session Expired")
            user = ''.join(random.choices(string.ascii_letters,k=10))
            session["user"] = user
            users[user] =  GeminiBot(role)
            user = session["user"] 
            
        if user_input:
            if test_assist:                 
                
                # query_embedding = embedding_model.encode([user_input])
                
                try:
                    # faiss_index, test_cases = get_data()
                    # D, I = faiss_index.search(np.array(query_embedding), k=5)
                    # results = test_cases.iloc[I[0]][["externalid", "summary", "preconditions", "combined_text"]].to_dict(orient="records")
                    # print("Faiss Search Results: ", results)
                    
                    results = vector_DB.get_nearest_match(os.getenv("Weaviate_Collection_Name"),user_input)
                    print("Weaviate Search Results: ", results)
                    
                    user_txt = json.dumps({"query": user_input, "results": results})

                    response = users[user].chat.send_message(user_txt)               
                    response_text = response.text
                    
                except Exception as e:
                    print(e)
                    
                    response_text = "Please add a Valid XML file and continue"
                
            else:
                response = users[user].chat.send_message(user_input)
                #followup_question makes LLM to ask follow up questions to users in required parts of a function call
                if response.candidates and response.candidates[0].content.parts[0].function_call:
                    text = users[user].handle_function_call(response)
                    
                    if text:
                        return jsonify({"response": text})
                
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
            # var = set_up_knowledge_base()
            Pass, fail = vector_DB.load_knowledge_base(os.getenv("Weaviate_Collection_Name"))
            
            return jsonify({"response": "Testcases Uploaded - "+Pass+" Failed Testcases Upload - "+fail})
        except:
            return jsonify({"response": "Mandatory fields are missing. Please import testlink exported XML file."}), 400

    else:
        return jsonify({"response": "File upload failed."}), 400

app.run(debug=True)  # Start the server
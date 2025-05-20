import csv
import xml.etree.ElementTree as ET
# from sentence_transformers import SentenceTransformer
import pandas as pd
# import faiss
import numpy as np
from app.services.tlink import Tlink
from app.constants import *

def xml_to_csv(xml_file, csv_file):
    '''
    Convert XML file to CSV format.
    '''
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Define base headers (non-step fields)
    base_headers = [
        "internalid", "name", "node_order", "externalid", "version", "summary",
        "preconditions", "execution_type", "importance"
    ]

    # Determine the maximum number of steps in any testcase
    max_steps = max(len(testcase.find('steps')) for testcase in root.findall('testcase') if testcase.find('steps') is not None)

    # Generate step headers dynamically
    step_headers = []
    for i in range(max_steps):
        step_headers.extend([
            f"steps/step/{i}/step_number",
            f"steps/step/{i}/actions",
            f"steps/step/{i}/expectedresults",
            f"steps/step/{i}/execution_type"
        ])

    # Combine base headers and step headers
    headers = base_headers + step_headers

    # Open the CSV file for writing
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

        # Iterate through each <testcase>
        for testcase in root.findall('testcase'):
            # Extract base data
            testcase_data = {
                "internalid": testcase.get('internalid'),
                "name": testcase.get('name'),
                "node_order": testcase.findtext('node_order', '').strip(),
                "externalid": testcase.findtext('externalid', '').strip(),
                "version": testcase.findtext('version', '').strip(),
                "summary": testcase.findtext('summary', '').strip(),
                "preconditions": testcase.findtext('preconditions', '').strip(),
                "execution_type": testcase.findtext('execution_type', '').strip(),
                "importance": testcase.findtext('importance', '').strip(),
            }

            # Extract step data
            steps = testcase.find('steps')
            if steps is not None:
                for i, step in enumerate(steps.findall('step')):
                    testcase_data.update({
                        f"steps/step/{i}/step_number": step.findtext('step_number', '').strip(),
                        f"steps/step/{i}/actions": step.findtext('actions', '').strip(),
                        f"steps/step/{i}/expectedresults": step.findtext('expectedresults', '').strip(),
                        f"steps/step/{i}/execution_type": step.findtext('execution_type', '').strip(),
                    })
                # Fill in missing steps with empty values
                for i in range(len(steps.findall('step')), max_steps):
                    testcase_data.update({
                        f"steps/step/{i}/step_number": "",
                        f"steps/step/{i}/actions": "",
                        f"steps/step/{i}/expectedresults": "",
                        f"steps/step/{i}/execution_type": "",
                    })
            else:
                # If no steps, fill all step columns with empty values
                for i in range(max_steps):
                    testcase_data.update({
                        f"steps/step/{i}/step_number": "",
                        f"steps/step/{i}/actions": "",
                        f"steps/step/{i}/expectedresults": "",
                        f"steps/step/{i}/execution_type": "",
                    })

            # Write the row to the CSV
            writer.writerow(testcase_data)

    print(f"CSV file '{csv_file}' has been created successfully.")

tlink = Tlink()
# Load Embedding Model
# embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
faiss_index =""
test_cases = ""

def get_data():
    return faiss_index, test_cases

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
        test_cases = load_test_cases("app/static/knowledge_base.csv")
        embeddings = embed_texts(test_cases["combined_text"].tolist())
        faiss_index = create_faiss_index(embeddings)

    except:
        return False
    return True

# def get_test_suites(testScenario):
def get_test_suites(testScenario, vector_DB):
    '''
    performs a semantic search on the tlink tree and returns the test suites
    '''
    # query_embedding = embedding_model.encode([arguments["testScenario"]])
    # query_embedding = embedding_model.encode([testScenario])
    # D, I = tree.search(np.array(query_embedding), k=5)
    # testSuites = df.iloc[I[0]].to_dict(orient="records")
    
    testSuites = vector_DB.get_nearest_match("Rently_Testsuites", testScenario, 10)
        
    ress = {}
    j=1
    for i in testSuites:        
        ress[str(j)] = i["testSuite_name"]
        j+=1
    
    # A followup question to user to select the test suite id
    # followup_question = "ask me where to create the test case?\n"+prompt+"\nask me to select the test suite id"
    
    return ress

    
def handle_role_change(curr_role, role, user):
    '''
    When ever user changes role of the bot,
    Existing chat session is closed and new chat session is created
    with the new role
    '''
    if role and curr_role != "test_assitant":
        user.create_new_chat(TEST_ASSISTANT)
        return "test_assitant"
    elif not role and curr_role != "bot":
        user.create_new_chat(BOT)
        return "bot"
    return curr_role

# Embed the tlink tree       
# df = pd.DataFrame(tlink_tree)
# tlink_embeddings = embed_texts(tlink_tree)
# tree = create_faiss_index(tlink_embeddings)
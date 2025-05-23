from google import genai
from google.genai import types
import os
import re
import json
from app.constants import *
from app.helpers.helper import *
from app.services.Weaviate import Weaviate
from dotenv import load_dotenv
from setup.GenerateTlinkTree import generate_tree
from setup.Bulk_import_to_weaviate import import_testcases

load_dotenv()
class GeminiBot:
    def __init__(self, role):
        self.client = genai.Client(api_key=os.getenv("GEMINI_KEY"))
        self.create_new_chat(role)
        self.vector_DB = Weaviate()
        

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
    
    def handle_function_call(self, response):
        '''
        Handles the function call from the response.
        and trigger appropriate function
        '''
            
        function_call = response.candidates[0].content.parts[0].function_call
        function_name = function_call.name
        print(f"Function: {function_name} triggered with arguments {function_call.args}")
        arguments = function_call.args  # Parse JSON arguments

        if function_name == "get_testsuite_id":
            print(response)
            res = get_test_suites(arguments["testScenario"], self.vector_DB)
        
        elif function_name == "generate_tlink_tree":
            result = generate_tree(arguments["project_id"])
            if result:
                res = {"result":"Testlink tree imported successfully"}
            else:
                res = {"result":"Error in importing testlink tree"}
        
        elif function_name == "bulk_importing_testcase":
            result = import_testcases(arguments["testsuite_id"], arguments["project_id"])
            if result:
                res = {"result":"Testlink testcases imported successfully"}
            else:
                res = {"result":"Error in importing testlink testcases"}
            
        elif function_name == "generate_testcase":                
            #Semantic search on the test cases to get impacted modules              
            impactedTestcases = self.vector_DB.get_nearest_match(os.getenv("Weaviate_Collection_Name"),arguments["testScenario"])
            
            testScenario = {"scenario": arguments["testScenario"], "related testcases":impactedTestcases}
            
            print("Impacted testcases: ", impactedTestcases)
            res = self.generate_testcase(json.dumps(testScenario))
        
        elif function_name == "create_testcase":
            try:
                print(arguments["acknowledgement"])
            except:
                return None, "Do you acknowledge generated testcases ?"
            
            print("creating testcases")
            print(arguments["generatedTestcases"])
            tlink.create_testcase(
                    testScenario=arguments["testScenario"],
                    testSuiteID=arguments["testSuiteID"],
                    Testcases = json.loads(arguments["generatedTestcases"]),
                )
            return "Created Testcases"
        else:
            print(f"Function {function_name} not implemented.")
            return "Failed Creatin testcase"
        
        function_response_part = types.Part(
                    function_response=types.FunctionResponse(
                        name=function_name,
                        # The response content needs to be a dict or compatible structure
                        response=res
                    )
                )

        response_after_tool = self.chat.send_message(function_response_part)
        return response_after_tool.text 

        
    
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
        print("After First filteration: \n"+op)
        
        return {"Generated testcases": op}

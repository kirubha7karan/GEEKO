from google import genai
from google.genai import types
import os
import json  # Import json for handling function call arguments
import re
from testlink import TestlinkAPIClient, TestLinkHelper, TestlinkAPIGeneric

# tl_helper = TestLinkHelper()
# tl_helper._server_url = 
# tl_helper._devkey = os.environ.get("TLINK_API_KEY")
# tlinkClient = tl_helper.connect(TestlinkAPIClient)

testlink_url = os.environ.get("TLINK_URL")
devkey = os.environ.get("TLINK__API_KEY")


        
# Create TestLink helper and API client
tlinkClient = TestLinkHelper(testlink_url, devkey).connect(TestlinkAPIClient)

System_instruction = "Generate structured test cases for the user given scenario \
Output should be in **JSON format** with the following fields:  \
\
- **test_case_title**: A concise title for the test case.  \
- **preconditions**: Any necessary setup or conditions before execution. \
- **steps**: A step-by-step procedure to execute the test case.  \
- **expected_results**: The expected outcome after executing the steps \" \
    After executing Step[1], expected_results[1] is expected. **count of steps and expected results should be always equal**\
\
### Example Output:\
[\
  {\
    \"test_case_title\": \"Login with valid credentials\",\
    \"preconditions\": \"User has a valid account.\",\
    \"steps\": [\
      \"Open the login page.\",\
      \"Enter valid username and password and Click the login button.\"\
    ],\
    \"expected_results\": [\" \
    \"the login page will be rendered\",\
    \"User successfully logs in and is redirected to the dashboard.\"\
  }\
]"
functions = [
    {
        "function_declarations": [
            {
                "name": "create_testcase",
                "description": "Creates testcase in testlink using testlink API",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "testScenario": {"type": "string", "description": "Scenario for which test case is created"},
                        "testCaseName": {"type": "string", "description": "Name of the testcase"},
                        "testSuiteID": {"type": "string", "description": "ID of the test suite"},
                        "testProjectID": {"type": "string", "description": "ID of the test project"},
                    },
                    "required": ["testScenario", "testCaseName", "testSuiteID", "testProjectID"],
                },
            }
        ]
    }
]

client = genai.Client(api_key=os.environ.get("GEMINI_KEY"))
chat = client.chats.create(
    model="gemini-2.0-flash",
    config=types.GenerateContentConfig(system_instruction="test_assistant", tools=functions, max_output_tokens=200),
)

def create_testcase(testScenario: str, testCaseName: str, testSuiteID: str, testProjectID: str):
    testcases = generate_testcase(testScenario)
    print("Creating Testcases")
    print(f"Test Case Name: {testCaseName}, Suite ID: {testSuiteID}, Project ID: {testProjectID}")
    i=0
    for testcase in testcases:
        testCaseName = testcase["test_case_title"]
        precondition = testcase["preconditions"]
        steps = testcase["steps"]
        expected_results = testcase["expected_results"]
        authorLogin="kirubakaran"
        tlinkClient.initStep(steps[0], expected_results[0], "manual")
        for i in range(1, len(steps)):
            tlinkClient.appendStep(steps[i], expected_results[i], "manual")

        # Here you would typically integrate with the TestLink API
        if i<2:
            tlinkClient.createTestCase(testCaseName, testSuiteID, testProjectID, authorLogin, testCaseName, preconditions=precondition, importance=2, executionType=1, estimatedExecDuration=0)
        i+=1
        print(f"Test Case {i} created successfully.")
def generate_testcase(Scenario):
    response = client.models.generate_content(
    model="gemini-2.0-flash",
    config=types.GenerateContentConfig(system_instruction=System_instruction),
    contents=[Scenario]
    )
    op = re.sub("```json","",response.text)
    op = re.sub("```","",op)

    print(op)


    return json.loads(op)


# Generate response (with function calling)
while True:
    user_prompt = input("User: ")
    if user_prompt == "/bye":
        break
    response = chat.send_message(user_prompt)

    if response.candidates and response.candidates[0].content.parts[0].function_call:
        function_call = response.candidates[0].content.parts[0].function_call
        function_name = function_call.name
        print(function_call.args)
        arguments = function_call.args  # Parse JSON arguments

        if function_name == "create_testcase":
            create_testcase(
                testScenario=arguments["testScenario"],
                testCaseName=arguments["testCaseName"],
                testSuiteID=arguments["testSuiteID"],
                testProjectID=arguments["testProjectID"],
            )
        else:
            print(f"Function {function_name} not implemented.")
    else:
        print("Bot: " + response.text)
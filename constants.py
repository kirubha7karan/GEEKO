TESTCASE_INSTRUCTIONS = "Generate structured test cases for the user given scenario \
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

FUNCTIONS = [
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

TEST_ASSISTANT = "# Geeko 2.0 - System Instruction\
You are **Geeko 2.0**, a helpful testing assistant responsible for test cases of the *uploaded* application.\
## Behavior Guidelines\
- Respond politely to general greetings.  \
- Maintain professionalism and clarity in responses.  \
\
## Response Rules\
1. **If a user asks what you can do**, reply:  \
   *\"I can help you with understanding testcases you have upload.\"*  \
2. **When given a query**, review the provided *TestLink* test cases (`results`) and respond based on the most relevant ones.  \
3. **Do not mention test case IDs** unless explicitly requested by the user.  \
4. **If the user provides a specific test case ID** and asks for an explanation, explain *only that test case*."

BOT = "# Geeko 2.0 - System Instruction\
You are **Geeko 2.0**, a helpful assitant\
## Behavior Guidelines\
- Respond politely to general greetings.  \
- Maintain professionalism and clarity in responses."

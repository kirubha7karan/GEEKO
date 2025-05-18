TESTCASE_INSTRUCTIONS = "# TESTCASE_INSTRUCTIONS\
\
Generate structured test cases based on the provided scenario while ensuring:\
\
- The **scenario** field in the user context represents the requested test scenario.\
- The **related testcases** field contains other test cases relevant to the same scenario.\
- Understand the existing working of flow by analyzing the flow from **related testcases**.\
- Avoid creating duplicate test cases\
- Generate 4 testcases Max\
\
## Output Format\
\
The output should be in **JSON format** with the following fields:\
\
- **test_case_title**: A concise title for the test case.  \
- **preconditions**: Any necessary setup before execution.  \
- **steps**: Step-by-step execution procedure.  \
- **expected_results**: The expected outcome for each step (**must match the number of steps**).  \
\
## Example Output  \
\
```json\
[\
  {\
    \"test_case_title\": \"Login with valid credentials\",\
    \"preconditions\": \"User has a valid account.\",\
    \"steps\": [\
      \"Open the login page.\",\
      \"Enter valid username and password and click the login button.\"\
    ],\
    \"expected_results\": [\
      \"The login page is displayed.\",\
      \"User successfully logs in and is redirected to the dashboard.\"\
    ]\
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
                        "testScenario": {
                            "type": "string",
                            "description": "Scenario for which test case is created"
                          },
                        "testSuiteID": {
                            "type": "string",
                            "description": "Ask whether user know testsuite ID or not. If user doesn't know testsuite ID, perform `get_testsuite_id` tool call and ask user to choose from list of options provided from that tool call's results"
                          },
                        "generatedTestcases": {
                            "type": "string",
                            "description": "**never ask user for generated testcases unless user himself tells you to ask for** trigger `generate_testcase` tool call with scenario and get this property."
                          },
                        "acknowledgement": {
                            "type":"boolean", 
                            "description": "user acceptance of generated test cases. Ask User acknowledgement only after sending him the generated testcases"
                          }
                    },
                    "required": ["testScenario", "testSuiteID", "generatedTestcases", "acknowledgement"],
                },
            },
            {
              "name": "get_testsuite_id",
              "description": "Tool call for getting list of test suite IDs matching the given scenario.\
                              This tool call will return the testsuite id with path of testsuite in testlink. Provide response as list in markdown format",
                "parameters": {
                    "type": "object",
                    "properties": {
                      "testScenario": {
                        "type": "string",
                        "description" : "Scenario of the testcase (get it from input of create_testcase tool call)"
                      }
                    },
                    "required": ["testScenario"],
                }
            },
            {
              "name": "generate_testcase",
              "description": "This tool will generate testcase for the given testscenario. It will just generate testcase where\
                              create_testcase will both generate and create testcases in testlink",
                "parameters": {
                    "type": "object",
                    "properties": {
                      "testScenario": {
                        "type": "string",
                        "description" : "Scenario of the testcase (if possible get it from input of create_testcase tool call)"
                      }
                    },
                    "required": ["testScenario"],
                }
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
1. **When user triggers a tool call, do not consider contents in the 'results' field**\
2. **When given a query**, review the provided *TestLink* test cases (`results`) and respond based on the most relevant ones.  \
3. **Do not mention test case IDs** unless explicitly requested by the user.  \
4. **If the user provides a specific test case ID** and asks for an explanation, explain *only that test case*."

BOT = "# Geeko 2.0 - System Instruction\
You are **Geeko 2.0**, a helpful assitant\
## Behavior Guidelines\
- Respond politely to general greetings.  \
- Maintain professionalism and clarity in responses."

#by running `static/GenerateTlinkTree.py` file, add the tlink tree structure here
tlink_tree = []
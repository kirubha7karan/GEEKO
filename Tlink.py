import os
from Gemini import GeminiBot
from testlink import TestlinkAPIClient, TestLinkHelper, TestlinkAPIGeneric

class Tlink:
    def __init__(self):
        testlink_url = os.getenv("TLINK_URL")
        devkey = os.getenv("TLINK_API_KEY")
        print(testlink_url,devkey)
        self.tlinkClient = TestLinkHelper(testlink_url, devkey).connect(TestlinkAPIClient)
    
    def create_testcase(self, testScenario: str, testCaseName: str, testSuiteID: str, testProjectID: str):
        try:
            print("creating testcase...")
            gemini = GeminiBot("test_case_generator")
            testcases = gemini.generate_testcase(testScenario)
            print("Creating Testcases")
            print(f"Test Case Name: {testCaseName}, Suite ID: {testSuiteID}, Project ID: {testProjectID}")
            i=0
            for testcase in testcases:
                print(f"Test Cases no. {i}.")
                
                testCaseName = testcase["test_case_title"]
                precondition = testcase["preconditions"]
                steps = testcase["steps"]
                expected_results = testcase["expected_results"]
                authorLogin="kirubakaran"
                self.tlinkClient.initStep(steps[0], expected_results[0], "manual")
                for j in range(1, len(steps)):
                    self.tlinkClient.appendStep(steps[j], expected_results[j], "manual")

                # Here you would typically integrate with the TestLink API
                if i<2:
                    tc_create = self.tlinkClient.createTestCase(testCaseName, testSuiteID, testProjectID, authorLogin, testCaseName, preconditions=precondition, importance=2, executionType=1, estimatedExecDuration=0)
                    print(f"Test Case {i} created successfully.")
                i+=1
            return True
        
        except Exception as e:
            print(e)
            return False
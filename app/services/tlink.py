import os
from testlink import TestlinkAPIClient, TestLinkHelper, TestlinkAPIGeneric
from dotenv import load_dotenv

load_dotenv()
class Tlink:
    def __init__(self):
        testlink_url = os.getenv("TLINK_URL")
        devkey = os.getenv("TLINK_API_KEY")
        self.tlinkClient = TestLinkHelper(testlink_url, devkey).connect(TestlinkAPIClient)
    
    def create_testcase(self, testScenario: str, testSuiteID: str, Testcases, testProjectID: str = "258561"):
        '''
        creates testcase in testlink using testlink API
        '''
        try:
            print("creating testcase...")
            print("TestScenario: "+testScenario)
            i=0
            for testcase in Testcases:
                print(f"Test Cases no. {i}.")
                
                testCaseName = testcase["test_case_title"]
                precondition = testcase["preconditions"]
                steps = testcase["steps"]
                expected_results = testcase["expected_results"]
                authorLogin=os.getenv("TLINK_USER_NAME")
                
                self.tlinkClient.initStep(steps[0], expected_results[0], "manual")
                for j in range(1, len(steps)):
                    self.tlinkClient.appendStep(steps[j], expected_results[j], "manual")

                # Restriction Just in case if the Generate testcase Agent generates more than 5 test cases
                # if i<5:
                tc_create = self.tlinkClient.createTestCase(testCaseName, testSuiteID, testProjectID, authorLogin, testCaseName, preconditions=precondition, importance=2, executionType=1, estimatedExecDuration=0)
                print(f"Test Case {i} created successfully.")
                i+=1
            return True, f"{len(Testcases)} Testcases created successfully."
        
        except Exception as e:
            print(e)
            return False, str(e)
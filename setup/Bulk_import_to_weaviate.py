import testlink
import csv
import os
import sys 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.Weaviate import Weaviate
from dotenv import load_dotenv

load_dotenv()
TESTLINK_API_KEY = os.getenv("TLINK_API_KEY")
TESTLINK_URL = os.getenv("TLINK_URL")
execution_type_map = {"1": "Manual", "2": "Automated","3": "To Be Automated"}
# Initialize TestLink API client
tlc = testlink.TestlinkAPIClient(TESTLINK_URL, TESTLINK_API_KEY)
PROJECT_ID = None

def get_methods():
    for method in testlink.testlinkargs._apiMethodsArgs.keys():
        print(tlc.whatArgs(method), '\n')

def decision(Execution_type, Automation_Reason):
    data = {
        "Type": execution_type_map.get(str(Execution_type), "N/A"),
        "Status": "N/A",
        "Automation Test Case ID": Automation_Reason,
        "Comments": "N/A",
    }
    if Execution_type == '1':
        data["Status"] = "Non Automatable"
        data["Automation Test Case ID"] = "N/A"
        data["Comments"] = Automation_Reason
    elif Execution_type == '2':
        data["Status"] = "Done"
        data["Automation Test Case ID"] = Automation_Reason
        data["Comments"] = "N/A"
    else:
        data["Status"] = "To Do"
        data["Automation Test Case ID"] = "N/A"
        data["Comments"] = Automation_Reason
    return data

def get_test_cases(suite_id, csv_writer, project_id, include_sub_suites=True):
    try:
        test_cases = tlc.getTestCasesForTestSuite(suite_id, include_sub_suites, 'full')
        for case in test_cases:
            custom_fields = tlc.getTestCaseCustomFieldDesignValue(
                testcaseid=case['id'],
                testprojectid=project_id,
                customfieldname="Automation Reason",
                details="simple",
                version=int(case['version'])
            )
            # value = decision(case['execution_type'], custom_fields['value'])
            # test_case_id = f'RM-{case.get("tc_external_id", "N/A")}'            # csv_writer.writerow([suite_name, case['id'], test_case_id, case['name'],value['Type'],value['Status'],value['Automation Test Case ID'],value['Comments'],test_case_url])
            writelist = [case['tc_external_id'], case['summary'], case['preconditions']]
            
            for step in case["steps"]:
                writelist.append(step["actions"])
                writelist.append(step["expected_results"])
                 
            
            csv_writer.writerow(writelist)
            
    except testlink.TestLinkError as e:
        print(f"TestLink API Error: {e}")
        return None


def get_suites(suite_id, csv_writer, project_id):
    try:
        get_test_cases(suite_id, csv_writer, project_id, False)
        child_suites = tlc.getTestSuitesForTestSuite(suite_id)
        if not child_suites == []: 
            for suite_id, suite_details in child_suites.items():
                get_test_cases(suite_id, csv_writer, project_id)
        else:
            print("Empty as expected")
    except testlink.TestLinkError as e:
        print(f"TestLink API Error: {e}")
        return None

    
def import_testcases(suite_id, project_id):
    try:
        csv_filename = f'{suite_id}_data.csv'

        with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
            csv_writer = csv.writer(file)
            # csv_writer.writerow(["Main Suite", "Internal ID", "Test Case ID", "Description", "Type", "Status", "Automation Test Case ID","Comments","Test Case Link"])
            csv_writer.writerow([
            "externalid", "summary", "preconditions",
            "steps/step/0/actions", "steps/step/0/expectedresults",
            "steps/step/1/actions", "steps/step/1/expectedresults",
            "steps/step/2/actions", "steps/step/2/expectedresults",
            "steps/step/3/actions", "steps/step/3/expectedresults",
            "steps/step/4/actions", "steps/step/4/expectedresults",
            "steps/step/5/actions", "steps/step/5/expectedresults",
            "steps/step/6/actions", "steps/step/6/expectedresults",
            "steps/step/7/actions", "steps/step/7/expectedresults",
            "steps/step/8/actions", "steps/step/8/expectedresults",
            "steps/step/9/actions", "steps/step/9/expectedresults",
            "steps/step/10/actions", "steps/step/10/expectedresults",
            "steps/step/11/actions", "steps/step/11/expectedresults",
            "steps/step/12/actions", "steps/step/12/expectedresults",
            "steps/step/13/actions", "steps/step/13/expectedresults",
            "steps/step/14/actions", "steps/step/14/expectedresults",
            "steps/step/15/actions", "steps/step/15/expectedresults",
            "steps/step/16/actions", "steps/step/16/expectedresults",
            "steps/step/17/actions", "steps/step/17/expectedresults",
            "steps/step/18/actions", "steps/step/18/expectedresults",
            "steps/step/19/actions", "steps/step/19/expectedresults",
            "steps/step/20/actions", "steps/step/20/expectedresults"])
            
            get_suites(suite_id, csv_writer, project_id)

        print(f"Data has been written to {csv_filename}")

        kb = Weaviate()
        kb.load_knowledge_base(os.getenv("Weaviate_Collection_Name"), csv_filename)
        kb.close_client()
        return True
    
    except Exception as e:
        print(e)
        return False

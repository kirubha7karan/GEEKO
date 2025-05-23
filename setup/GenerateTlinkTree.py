'''
Run this file and assign it to `tlink_tree` list constants.py file
'''
from testlink import TestlinkAPIClient
import os
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.Weaviate import Weaviate

load_dotenv()
# Replace with your TestLink server details
TESTLINK_URL = os.getenv("TLINK_URL")
API_KEY = os.getenv("TLINK_API_KEY")

tl = TestlinkAPIClient(TESTLINK_URL, API_KEY)

def get_test_suites(project_name):
    testsuites = []
    project = next((p for p in tl.getProjects() if p['name'] == project_name), None)
    if not project:
        print(f"Project '{project_name}' not found.")
        return
    
    project_id = project['id']
    suites = tl.getFirstLevelTestSuitesForTestProject(project_id)

    def build_hierarchy(suite, parent_path=""):
        try:
            suite_id = suite['id']
            suite_name = suite['name']
            full_path = f"{parent_path}->{suite_name}" if parent_path else suite_name
            children = tl.getTestSuitesForTestSuite(suite_id)
            if children:
                for child in children.values():
                    build_hierarchy(child, full_path)
            else:
                testsuites.append(f"{project_name} -> {full_path} -> {suite_id}")
                print(f"{project_name} -> {full_path} -> {suite_id}")
        except:
            testsuites.append(f"{project_name} -> {full_path} -> {suite_id}")
            print(f"{project_name} -> {full_path} -> {suite_id}")
            

    for suite in suites:
        build_hierarchy(suite)
    
    return testsuites

# Replace 'Your_Project_Name' with your actual project name
# Project = input("Enter Project Name: ") #eg: Master

def generate_tree(project_id):
    try:
        testsuites = get_test_suites(project_id)

        kb = Weaviate()
        res = kb.load_tlink_tree(os.getenv("Weaviate_Tree_Name"), testsuites)
        kb.close_client()
        return res
    
    except Exception as e:
        print(e)
        return False
        
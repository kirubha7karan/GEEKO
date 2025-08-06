from jira import JIRA
import os

class jiraIssues:
    def __init__(self):
        self.jira_domain = os.getenv("JIRA_DOMAIN")
        self.email = os.getenv("JIRA_EMAIL")
        self.api_token = os.getenv("JIRA_API_KEY")
        self.jira = JIRA(
            server=self.jira_domain,
            basic_auth=(self.email, self.api_token)
        )

    def get_issue(self, issue_key):
        issue = self.jira.issue(issue_key)
        return {
            "summary": issue.fields.summary,
            "description": issue.fields.description
        }
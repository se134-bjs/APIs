import requests
from requests.auth import HTTPBasicAuth

class AtlassianAssistant:
    def __init__(self, domain, email, token):
        # These make the code work for "Every User" dynamically
        self.base_url = f"https://{domain}.atlassian.net"
        self.auth = HTTPBasicAuth(email, token)
        self.headers = {"Accept": "application/json", "Content-Type": "application/json"}

    # --- JIRA ENDPOINTS ---
    
    def get_my_open_issues(self):
        """Fetches 'Open' tasks for the current user """
        url = f"{self.base_url}/rest/api/3/search"
        # JQL is dynamic: only shows tasks assigned to the person logged in
        query = {'jql': 'assignee = currentUser() AND statusCategory != Done'}
        response = requests.get(url, auth=self.auth, params=query, headers=self.headers)
        return response.json()

    def get_sprint_progress(self, sprint_id):
        """Objective 1: Provide real-time sprint summaries """
        url = f"{self.base_url}/rest/agile/1.0/sprint/{sprint_id}/issue"
        response = requests.get(url, auth=self.auth, headers=self.headers)
        return response.json()

    # --- CONFLUENCE ENDPOINTS ---

    def create_automation_page(self, title, html_content, space_key):
        """Objective 2: Auto-generate SRS, Backlog, or Risk Registers [cite: 16, 21]"""
        url = f"{self.base_url}/wiki/rest/api/content"
        payload = {
            "type": "page",
            "title": title,
            "space": {"key": space_key},
            "body": {"storage": {"value": html_content, "representation": "storage"}}
        }
        response = requests.post(url, auth=self.auth, json=payload, headers=self.headers)
        return response.json()

# --- Example Usage for the 'Smart' Chatbot ---
user_bot = AtlassianAssistant("your-domain", "user@email.com", "API_TOKEN_1")
issues = user_bot.get_my_open_issues()


for issue in issues['issues']:
    print(f"Task: {issue['key']} - {issue['fields']['summary']}")
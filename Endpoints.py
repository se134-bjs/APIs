import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ProjectAssistant:
    def __init__(self):
        # Jira/Confluence Setup
        self.jira_domain = os.getenv("JIRA_DOMAIN")
        self.jira_email = os.getenv("JIRA_EMAIL")
        self.jira_token = os.getenv("JIRA_TOKEN")
        self.jira_auth = HTTPBasicAuth(self.jira_email, self.jira_token)
        
        # Trello Setup
        self.trello_key = os.getenv("TRELLO_API_KEY")
        self.trello_token = os.getenv("TRELLO_TOKEN")
        
        self.headers = {"Accept": "application/json", "Content-Type": "application/json"}

    # --- DYNAMIC JIRA ENDPOINTS ---
    
    def get_tasks(self, jql="assignee = currentUser() AND statusCategory != Done"):
        """Fetches Jira tasks dynamically based on JQL [cite: 15]"""
        url = f"https://{self.jira_domain}.atlassian.net/rest/api/3/search/jql"
        response = requests.get(url, auth=self.jira_auth, params={'jql': jql}, headers=self.headers)
        return response.json()

    # --- DYNAMIC TRELLO ENDPOINTS ---

    def get_trello_cards(self, list_id=None):
        """Fetches cards from a specific Trello list. If no ID is provided, uses .env default."""
        target_list = list_id or os.getenv("TRELLO_LIST_ID")
        url = f"https://api.trello.com/1/lists/{target_list}/cards"
        query = {'key': self.trello_key, 'token': self.trello_token}
        
        response = requests.get(url, params=query)
        return response.json()

    # --- CONFLUENCE AUTOMATION ---

    def create_confluence_page(self, title, html_content, space_key="PROJ"):
        """Auto-generates documentation pages like SRS or Backlogs [cite: 16, 21]"""
        url = f"https://{self.jira_domain}.atlassian.net/wiki/rest/api/content"
        payload = {
            "type": "page",
            "title": title,
            "space": {"key": space_key},
            "body": {"storage": {"value": html_content, "representation": "storage"}}
        }
        response = requests.post(url, auth=self.jira_auth, json=payload, headers=self.headers)
        return response.json()

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    bot = ProjectAssistant()
    
    print(f"--- Checking Jira Tasks for {bot.jira_domain} ---")
    jira_data = bot.get_tasks()
    
    if 'issues' in jira_data:
        for issue in jira_data['issues']:
            print(f"Jira Task: {issue['key']} - {issue['fields']['summary']}")
    else:
        print("Jira Error:", jira_data)

    print(f"\n--- Checking Trello Cards for List ID: {os.getenv('TRELLO_LIST_ID')} ---")
    trello_cards = bot.get_trello_cards()
    
    if isinstance(trello_cards, list):
        for card in trello_cards:
            print(f"Trello Card: {card['name']}")
    else:
        print("Trello Error:", trello_cards)
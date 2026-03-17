import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

class DynamicAssistant:
    def __init__(self):
        # Jira Config
        self.jira_domain = os.getenv("JIRA_DOMAIN")
        self.jira_email = os.getenv("JIRA_EMAIL")
        self.jira_token = os.getenv("JIRA_TOKEN")
        self.jira_auth = HTTPBasicAuth(self.jira_email, self.jira_token)
        
        # Trello Config
        self.trello_key = os.getenv("TRELLO_API_KEY")
        self.trello_token = os.getenv("TRELLO_TOKEN")
        
        self.headers = {"Accept": "application/json", "Content-Type": "application/json"}

    # --- JIRA METHODS ---
    def get_tasks(self, jql='project = "KAN"'):
        """Fetches issues from Jira. Defaulted to your 'KAN' project from the screenshot."""
        url = f"https://{self.jira_domain}.atlassian.net/rest/api/3/search/jql"
        
        params ={
            'jql':jql,
            'fields': 'summary,status,issuetype'
        }
        response = requests.get(url, auth=self.jira_auth, params=params, headers=self.headers)
        return response.json()

    # --- TRELLO HIERARCHY METHODS (Your new control flow) ---
    def get_trello_boards(self):
        """Step 1: Get all Boards"""
        url = "https://api.trello.com/1/members/me/boards"
        query = {'key': self.trello_key, 'token': self.trello_token}
        response = requests.get(url, params=query)
        return response.json()

    def get_trello_lists(self, board_id):
        """Step 2: Get Lists for a specific Board"""
        url = f"https://api.trello.com/1/boards/{board_id}/lists"
        query = {'key': self.trello_key, 'token': self.trello_token}
        response = requests.get(url, params=query)
        return response.json()

    def get_trello_cards(self, list_id):
        """Step 3: Get Cards for a specific List"""
        # Fallback to .env if no list_id is passed
        # target_list = list_id or os.getenv("TRELLO_LIST_ID")
        url = f"https://api.trello.com/1/lists/{list_id}/cards"
        query = {'key': self.trello_key, 'token': self.trello_token}
        response = requests.get(url, params=query)
        return response.json()

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    bot = DynamicAssistant()

    # 1. Test Jira (Project KAN)
    print(f"--- Checking Jira Tasks for {bot.jira_domain} ---")
    jira_data = bot.get_tasks(jql='project="KAN"') # Now this attribute exists!
    
    if 'issues' in jira_data and isinstance(jira_data['issues'], list):
        issues_found = jira_data['issues']
        print(f"Total issues found {len(issues_found)}")
        for issue in issues_found:
            if 'key' in issue and 'fields' in issue:
                key = issue['key']
                summary = issue.get('fields',{}).get('summary','No Summary Provided')
                print(f"Jira Task: {key} - {summary}")
            else:
                print(f"Skipping malformed issue entry:{issue}")
                
    else:
        print("No issues found or API Error. Raw response:", jira_data)

    # 2. Test Trello Dynamic Control
    print("\n--- Trello Board Control ---")
    boards = bot.get_trello_boards()
    
    
    if isinstance(boards, list):
        print("Your Available Boards:")
        for index, board in enumerate(boards):
            print(f"{index}: {board['name']} (ID: {board['id']})")
        
        # Dynamic Selection
        choice = input("\nEnter the number of the board you want to explore: ")
        selected_board = boards[int(choice)]
        
        print(f"\n--- Fetching Lists for Board: {selected_board['name']} ---")
        lists = bot.get_trello_lists(selected_board['id'])
        
        if isinstance(lists, list):
            for l in lists:
                print(f"List Found: {l['name']} (ID: {l['id']})")
                
                # Optionally: uncomment to see cards for every list automatically
                # cards = bot.get_trello_cards(l['id'])
                # for card in cards:
                #     print(f"  -> Card: {card['name']}")
    else:
        print("Could not retrieve boards:", boards)
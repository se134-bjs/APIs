import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

class DynamicAssistant:
    def __init__(self):
        
        self.base_url = os.getenv("base_url")
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
        url = f"{self.base_url}members/me/boards"
        query = {'key': self.trello_key, 'token': self.trello_token}
        response = requests.get(url, params=query)
        return response.json()

    def get_trello_lists(self, board_id):
        """Step 2: Get Lists for a specific Board"""
        url = f"{self.base_url}boards/{board_id}/lists"
        query = {'key': self.trello_key, 'token': self.trello_token}
        response = requests.get(url, params=query)
        return response.json()

    def get_trello_cards(self, list_id):
        """Step 3: Get Cards for a specific List"""
        # Fallback to .env if no list_id is passed
        # target_list = list_id or os.getenv("TRELLO_LIST_ID")
        url = f"{self.base_url}lists/{list_id}/cards"
        query = {'key': self.trello_key, 'token': self.trello_token}
        response = requests.get(url, params=query)
        return response.json()
    
    def get_card_details(self, card_id):
        """Fetches full card metadata including description, labels, and checklists."""
        url = f"{self.base_url}cards/{card_id}"
        query = {
            'key': self.trello_key,
            'token': self.trello_token,
            # We explicitly ask for these fields to match your UI screenshot
            'fields': 'name,desc,due,labels',
            'checklists': 'all',
            'members': 'true',
            'actions':'commentCard'
        }
        response = requests.get(url, params=query)
        return response.json()

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    bot = DynamicAssistant()

    while True:
        print("\n=== TRELLO MAIN MENU (BOARDS) ===")
        boards = bot.get_trello_boards()
        
        for i, b in enumerate(boards, 1): # Start indexing at 1
            print(f"{i}. {b['name']}")
        print("0. Exit Program")

        b_choice = input("\nSelect a Board (or 0 to Exit): ")
        if b_choice == '0': break
        
        # Get selected board
        board = boards[int(b_choice) - 1]

        while True:
            print(f"\n--- BOARD: {board['name']} (LISTS) ---")
            lists = bot.get_trello_lists(board['id'])
            
            for i, l in enumerate(lists, 1):
                print(f"{i}. {l['name']}")
            print("0. BACK to Boards")

            l_choice = input("\nSelect a List to see Cards (or 0 for Back): ")
            if l_choice == '0': break # This breaks the List loop and goes back to Board loop

            # Get selected list
            selected_list = lists[int(l_choice) - 1]
            
            print(f"\n--- LIST: {selected_list['name']} (CARDS) ---")
            cards = bot.get_trello_cards(selected_list['id'])
            
            if not cards:
                print("   (No cards found in this list)")
            else:
                for i, card in enumerate(cards,1):
                    print(f"  {i}.[Card] {card['name']}")
                    
                    # ... (Inside the List loop after cards are displayed) ...
            c_choice = input("\nSelect a Card number to see Details (or 0 for Back): ")
            if c_choice == '0': break
            
            # Fetch the specific card chosen by the user
            selected_card = cards[int(c_choice) - 1]
            details = bot.get_card_details(selected_card['id'])

            print(f"\n{'='*40}")
            print(f" CARD DETAIL: {details.get('name')}")
            print(f"{'='*40}")
            print(f"Description: {details.get('desc') or 'No description provided.'}")
            print(f"Due Date:    {details.get('due') or 'No date set'}")
            
            # Display Labels
            labels = [l['name'] if l['name'] else l['color'] for l in details.get('labels', [])]
            print(f"Labels:      {', '.join(labels) if labels else 'None'}")

            # Display Checklists (from your screenshot's Checklist button)
            checklists = details.get('checklists', [])
            if checklists:
                print("\n--- Checklists ---")
                for cl in checklists:
                    print(f"[{cl['name']}]")
                    for item in cl['checkItems']:
                        status = "X" if item['state'] == 'complete' else " "
                        print(f"  [{status}] {item['name']}")
            
            comments = details.get('actions', [])
            if comments:
                # print("\n--- Recent Comments ---")
                for c in comments:
                    user = c['memberCreator']['fullName']
                    text = c['data']['text']
                    # date = c['date'][:10] # Just the YYYY-MM-DD
                    print(f"Comments: {text}")
                    # print(f"  {user} ({date}): {text}")
            
            input("\nPress Enter to go back to the list...")
            
            # input("\nPress Enter to return to List menu...")
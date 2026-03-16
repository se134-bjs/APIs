import requests

import os #importing os module for environmental variable
from dotenv import load_dotenv , dotenv_values #importing necessary functions from dotenv library
load_dotenv() #loading variables from .env file

# print(os.getenv("API_KEY"))
# print(os.getenv("TOKEN"))

# --- CONFIGURATION ---

LIST_ID=os.getenv("LIST_ID")
# --- THE REQUEST ---
url = f"https://api.trello.com/1/lists/{LIST_ID}/cards"

query = {
    'key': os.getenv("API_KEY"), #API_KEY,
    'token': os.getenv("TOKEN") #TOKEN
}

response = requests.get(url, params=query)

# print("Responce")
# print(response.json())

# --- THE LOGIC ---
if response.status_code == 200:
    cards = response.json()
    # print(f"cards {cards}")
    print(f"--- Found {len(cards)} cards ---")
    
    # for card in cards:
    #     print(f"• Card Name {card['name']}")
    #     print(f"• Card Id {card['id']}")
    #     print(f"• Card Agent {card['agent']}")
    #     print(f"• Card Badges{card['badges']}")
    for card in cards:
        print(f"• Card Name: {card['name']}")
        # Digging into the nested 'badges' dictionary
        comment_count = card['badges']['comments']
        print(f"  └─ Comments: {comment_count}")
        
        # Digging even deeper into 'attachmentsByType' -> 'trello'
        trello_attachments = card['badges']['attachmentsByType']['trello']['card']
        print(f"  └─ Trello Card Attachments: {trello_attachments}")
else:
    print(f"Error: {response.status_code}")
    
    
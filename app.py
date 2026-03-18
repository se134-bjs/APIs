import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from Endpoints import DynamicAssistant # Assuming your class is in logic.py
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


app = Flask(__name__)
bot = DynamicAssistant()

chat_histories = {}

tools = [
    bot.get_tasks,
    bot.get_trello_boards,
    bot.get_trello_lists,
    bot.get_trello_cards
]

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    tools=tools
)

@app.route('/api/chat', methods=['POST'])
def smart_assistant():
    data=request.json
    user_prompt = data.get('prompt')
    user_id = data.get('user_id','default_user')
    
    # Retrive existing history from the user
    existing_history = chat_histories.get(user_id, [])
    
    # Start chat with the history
    chat = model.start_chat(
        history=existing_history,
        enable_automatic_function_calling=True
    )
    
    # user_prompt = request.json.get('prompt')
    
    # chat=model.start_chat(enable_automatic_function_calling=True)
    
    response = chat.send_message(user_prompt)
    
    chat_histories[user_id] = chat.history
    return jsonify({
        "answer":response.text
    })

# --- JIRA ENDPOINTS ---

@app.route('/api/jira/tasks', methods=['GET'])
def get_jira_tasks():
    project = request.args.get('project', 'KAN')
    tasks = bot.get_tasks(jql=f'project = "{project}"')
    return jsonify(tasks)

# --- TRELLO ENDPOINTS ---

@app.route('/boards', methods=['GET'])
def get_boards():
    boards = bot.get_trello_boards()
    # We return JSON so a frontend or Postman can read it
    return jsonify(boards)

@app.route('/board/<board_id>/lists', methods=['GET'])
def get_lists(board_id):
    lists = bot.get_trello_lists(board_id)
    return jsonify(lists)

@app.route('/lists/<list_id>/cards', methods=['GET'])
def get_cards(list_id):
    cards = bot.get_trello_cards(list_id)
    return jsonify(cards)

@app.route('/cards/<card_id>', methods=['GET'])
def get_card_info(card_id):
    details = bot.get_card_details(card_id)
    return jsonify(details)

if __name__ == '__main__':
    # Run the server on localhost:5000
    app.run(debug=True)
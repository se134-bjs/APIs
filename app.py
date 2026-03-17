from flask import Flask, jsonify, request
from Endpoints import DynamicAssistant # Assuming your class is in logic.py

app = Flask(__name__)
bot = DynamicAssistant()

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
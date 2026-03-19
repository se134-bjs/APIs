import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from Endpoints import DynamicAssistant # Assuming your class is in logic.py
import google.generativeai as genai
import json
# from openai import OpenAI
from groq import Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

load_dotenv()
# genai.configure(api_key=os.getenv("GROQ_API_KEY"))


app = Flask(__name__)
bot = DynamicAssistant()

chat_histories = {}

tools = [
    bot.get_tasks,
    bot.get_trello_boards,
    bot.get_trello_lists,
    bot.get_trello_cards
]

tools_schema = [
    {
        "type":"function",
        "function":{
            "name":"get_tasks",
            "description":"desc",
            "parameters":{"type":"object", "properties":{"jql":{"type":"string"}}}
        }
    },
    {
        "type":"function",
        "function":{
            "name":"get_trello_boards",
            "description":"desc",
            "parameters":{"type":"object", "properties":{"jql":{"type":"string"}}}
        }
    },
    {
        "type":"function",
        "function":{
            "name":"get_trello_lists",
            "description":"desc",
            "parameters":{"type":"object", "properties":{"jql":{"type":"string"}}}
        }
    },
    {
        "type":"function",
        "function":{
            "name":"get_trello_cards",
            "description":"desc",
            "parameters":{"type":"object", "properties":{"jql":{"type":"string"}}}
        }
    }
]
#declaring the model outside the endpoint means it is in global scope
# model = genai.GenerativeModel(
#     model_name='gemini-2.5-flash',
#     tools=tools
# )

@app.route('/api/chat', methods=['POST'])
def smart_assistant():
    data=request.json
    user_prompt = data.get('prompt')
    user_id = data.get('user_id','default_user')
    
    # Maintain history in OpenAI format(lists of messages)
    history = chat_histories.get(user_id, [])
    history.append({"role":"user", "content": user_prompt})
    
    # Step 1 : send the prompt to openai
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=history,
        tools=tools_schema,
        tool_choice="auto"
    )
    
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    
    # Step 2 : Handle function calling (The "Efficency" part )
    if tool_calls:
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            
            # Map the AI request to you DynamicAssistant method
            args=json.loads(tool_call.function.arguments or "{}")
            
            if function_name == "get_tasks":
                result = bot.get_tasks(jql=args.get("jql",'project="KAN"'))
            
            elif function_name == "get_trello_boards":
                result = bot.get_trello_board()
            
            elif function_name == "get_trello_lists":
                result = bot.get_trello_lists(args.get("board_id"))
            
            elif function_name == "get_trello_cards":
                result = bot.get_trello_cards(args.get("list_id"))
            
            else:
                result="Function Not Found"
                
            # Feed the data back to OpenAI so it can answer the user
            history.append(response_message)
            history.append({
                "role":"tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": str(result)
            })
            
            # Get final answer from AI
            second_response=client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=history
            )
            final_content = second_response.choices[0].message.content
    else:
        final_content = response.choices[0].message.content
        
    # Save the history and return
    history.append({"role":"assistant", "content":final_content})
    chat_histories[user_id]=history
    
    return jsonify({"answer":final_content})
            
    
    # Start chat with the history
    # chat = model.start_chat(
    #     history=existing_history,
    #     enable_automatic_function_calling=True
    # )
    
    # user_prompt = request.json.get('prompt')
    
    # chat=model.start_chat(enable_automatic_function_calling=True)
    
    # response = chat.send_message(user_prompt)
    
    # chat_histories[user_id] = chat.history
    # return jsonify({
    #     "answer":response.text
    # })

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
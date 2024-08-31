from flask import Blueprint, request, jsonify
from .analysis import analyze_request, generate_charts, extract_stock_symbol_groq

# Define a blueprint for the main routes
main = Blueprint('main', __name__)
@main.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("message")
    chat_history = data.get("history", [])
    if user_message:
        # Perform analysis, passing the chat history
        response_text, updated_history, charts = analyze_request(user_message, chat_history)
        chart_path = None
        if charts == 1:
            stock_symbol = extract_stock_symbol_groq(user_message)
            if stock_symbol:
                print(stock_symbol)
                chart_path = generate_charts(stock_symbol, "monthly")
            else:
                chart_path = None
    else:
        response_text = "Sorry, I couldn't identify any message. Please ask about a specific stock."
        chart_path = None

    return jsonify({"response": response_text, "chart": chart_path, "history": updated_history})

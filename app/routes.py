from flask import Blueprint, request, jsonify
from .analysis import analyze_request, generate_charts, analyze_news, extract_stock_symbol_groq, analyze_stock

# Define a blueprint for the main routes
main = Blueprint('main', __name__)

@main.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message")
    
    if user_message:
        # Perform stock analysis if a valid stock symbol is found
        analysis_result = analyze_request(user_message)
        stock_symbol = extract_stock_symbol_groq(user_message)
        chart_path = generate_charts(stock_symbol, "monthly")
        response_text = f"{analysis_result}"
    else:
        response_text = "Sorry, I couldn't identify a stock symbol in your message. Please ask about a specific stock."

    return jsonify({"response": response_text, "chart": chart_path})

@main.route('/analyze/<string:stock_symbol>', methods=['GET'])
def analyze(stock_symbol):
    if stock_symbol:
        # Perform stock analysis
        analysis_result = analyze_stock(stock_symbol)
        
        # Generate charts based on analysis
        charts = generate_charts(analysis_result)
        
        return jsonify({
            "analysis": analysis_result,
            "charts": charts
        })
    else:
        return jsonify({"error": "No stock symbol provided."}), 400

@main.route('/news/<string:company_name>', methods=['GET'])
def news(company_name):
    if company_name:
        # Perform news analysis
        news_analysis = analyze_news(company_name)
        return jsonify({"news_analysis": news_analysis})
    else:
        return jsonify({"error": "No company name provided."}), 400

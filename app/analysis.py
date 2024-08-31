import json
import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
from groq import Groq


ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

def analyze_request(user_message, chat_history):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    charts = 0
    if "stock" in user_message.lower() or "price" in user_message.lower() or "market" in user_message.lower():
        stock_symbol = extract_stock_symbol_groq(user_message)
        stock_analysis = analyze_stock(stock_symbol)
        response_text = f"Analyis:\n{stock_analysis}"
        news_analysis = analyze_news(stock_symbol)
        response_text += f"\n\nNews analysis:\n{news_analysis}"
        chat_history.append({"role": "assistant", "content": response_text})
        charts = 1
    else:
        # Append the user's message to the chat history
        chat_history.append({"role": "user", "content": user_message})
        if len(chat_history) > 3:
            chat_history = chat_history[-3:]
        histories = ""
        # Generate a generic response using the entire chat history
        for dicts in chat_history:
            histories += json.dumps(dicts)

        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{
                'role': "user", "content": f"This is is the history: {histories}. The new message: {user_message}. Reply to the new message. Just analyse the history, and normally answer the new message. Do not answer in dictionary format. Just tell the current answer only. Do not tell about the histories. Analysis is only for you to learn, not to showcase in output."
            }]
        )
        
        # Capture Groq's response and append it to the chat history
        generic_response = ""
        generic_response += response.choices[0].message.content or ""
        
        chat_history.append({"role": "assistant", "content": generic_response})
        
        response_text = generic_response
    
    return response_text, chat_history, charts

def extract_stock_symbol_groq(user_message):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "user", "content": f"Extract the stock symbol from this message: '{user_message}'. If the company name is given, then just return it's respective stock symbol only."}
        ]
    )
    symbol = ""
    symbol += response.choices[0].message.content or ""
    
    symbol = symbol.strip().upper()
    
    
    return symbol

def analyze_stock(stock_symbol):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "user", "content": f"Analyze the stock performance of {stock_symbol}. Limit yourself , and give answers in a limited manner."}
        ]
    )
    analysis_result = ""
    analysis_result += response.choices[0].message.content or ""
    return analysis_result

def generate_charts(stock_symbol, time_series="monthly"):
    # Ensure that Matplotlib doesn't try to use any GUI backend
    plt.switch_backend('Agg')

    # Set the function name based on the time series type
    function_name = "TIME_SERIES_MONTHLY" if time_series == "monthly" else "TIME_SERIES_WEEKLY"
    
    ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
    url = f"https://www.alphavantage.co/query?function={function_name}&symbol={extract_stock_symbol_groq(stock_symbol)}&apikey={ALPHA_VANTAGE_API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    if "subscribe" in data:
        return None
    if "Monthly Time Series" in data:
        time_series_data = data["Monthly Time Series"]
    elif "Weekly Time Series" in data:
        time_series_data = data["Weekly Time Series"]
    else:
        return None  # No data available, return None instead of a string

    # Convert the time series data into a DataFrame
    df = pd.DataFrame.from_dict(time_series_data, orient='index')
    df = df.rename(columns={"4. close": "Close"})
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    # Plot the data using matplotlib
    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df['Close'].astype(float), marker='o', linestyle='-')
    plt.title(f"{stock_symbol} Stock Price ({time_series.capitalize()})")
    plt.xlabel("Date")
    plt.ylabel("Closing Price")
    
    # Ensure the static directory exists
    if not os.path.exists('static'):
        os.makedirs('static')

    chart_path = f"static/{stock_symbol}_{time_series}_chart.png"
    plt.savefig(chart_path)
    plt.close()
    
    return chart_path


def analyze_news(company_name):
    # Get the API key from environment variables
    api_key = os.getenv("NEWS_API")
    if not api_key:
        raise ValueError("NEWS_API_KEY environment variable is not set.")
    
    # Define the endpoint and parameters
    url = "https://newsapi.org/v2/everything"
    params = {
        'q': company_name,
        'language': 'en',
        'sortBy': 'relevancy',
        'apiKey': api_key
    }
    
    # Make the GET request to the NewsAPI
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return f"Error fetching news: {e}"
    
    # Parse the JSON response
    articles = response.json().get('articles', [])
    
    if not articles:
        return "No news articles found for the given company."

    # Generate a summary of the news articles
    news_summary = ""
    for article in articles:
        title = article.get('title', 'No Title')
        description = article.get('description', 'No Description')
        url = article.get('url', 'No URL')        
        # Analyze how the news might affect stock value
        news_analysis = analyze_stock_effect(title + description, company_name)
        news_summary += f"Potential Impact on Stock: {news_analysis}\n\n"

    return news_summary


def analyze_stock_effect(news_text, stock_symbol):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "user", "content": f"Analyze how this news affects the stock value of the stock of {stock_symbol}: {news_text}. Be very concise."}
        ]
    )
    analysis_result = ""
    analysis_result += response.choices[0].message.content or ""
    return analysis_result

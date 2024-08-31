import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
from groq import Groq
import re

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

def analyze_request(user_message):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    if "stock" in user_message.lower() or "price" in user_message.lower() or "market" in user_message.lower():
        stock_symbol = extract_stock_symbol_groq(user_message)
        print(stock_symbol)
        stock_analysis = analyze_stock(stock_symbol)
        response_text = f"The analysis for {stock_symbol}:\n {stock_analysis}"
        news_analysis = analyze_news(stock_symbol)
        response_text += f"\n\n\n\n\n\nNews analysis for {stock_symbol}: {news_analysis}"
    else:
        response_text = "I'm here to help you with stock and news analysis. Please specify what you would like to know."
    
    return response_text

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
    
    # Fallback with regex if the symbol extracted is empty or seems incorrect
    if not symbol or not re.match(r'^[A-Z]{1,5}$', symbol):
        match = re.search(r'\b[A-Z]{1,5}\b', user_message.upper())
        symbol = match.group(0) if match else None
    
    return symbol

def analyze_stock(stock_symbol):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "user", "content": f"Analyze the stock performance of {stock_symbol}."}
        ]
    )
    analysis_result = ""
    analysis_result += response.choices[0].message.content or ""
    return analysis_result

def generate_charts(stock_symbol, time_series="monthly"):
    # Set the function name based on the time series type
    function_name = "TIME_SERIES_MONTHLY" if time_series == "monthly" else "TIME_SERIES_WEEKLY"
    
    url = f"https://www.alphavantage.co/query?function={function_name}&symbol={extract_stock_symbol_groq(stock_symbol)}&apikey={ALPHA_VANTAGE_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if "Monthly Time Series" in data:
        time_series_data = data["Monthly Time Series"]
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
    
    chart_path = f"./static/{stock_symbol}_{time_series}_chart.png"
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
        'pageSize': 5,  # Limit to 5 articles for brevity
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
            {"role": "user", "content": f"Analyze how this news affects the stock value of the stock of {stock_symbol}: {news_text}"}
        ]
    )
    analysis_result = ""
    analysis_result += response.choices[0].message.content or ""
    return analysis_result

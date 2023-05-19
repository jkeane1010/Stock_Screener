from alpha_vantage.timeseries import TimeSeries
import plotly.graph_objs as go
import requests

ALPHA_VANTAGE_API_KEY = "T4BWDWX4X7DAUBQO"


def fetch_stock_data(stock_symbol):
    try:
        ts = TimeSeries(key=ALPHA_VANTAGE_API_KEY, output_format="pandas")
        data, _ = ts.get_daily_adjusted(stock_symbol, outputsize="compact")
        data = data.iloc[::-1]
        # Extract the last close price
        last_close_price = data['4. close'].iloc[-1]
        return data, last_close_price
    except Exception:
        return None, None


def get_company_financials(stock_symbol):
    api_url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={stock_symbol}&apikey=" \
              f"{ALPHA_VANTAGE_API_KEY}"

    response = requests.get(api_url)
    data1 = response.json()

    financial_year = None
    description = None
    year_week_high = None
    year_week_low = None
    short_MA = None
    long_MA = None

    if "RevenueTTM" in data1 and "MarketCapitalization" in data1 and "GrossProfitTTM" in data1:
        revenue = data1["RevenueTTM"]
        market_cap = data1["MarketCapitalization"]
        gross_profit = data1["GrossProfitTTM"]
        financial_year = data1["LatestQuarter"]
        description = data1["Description"]
        year_week_high = data1["52WeekHigh"]
        year_week_low = data1["52WeekLow"]
        short_MA = data1["50DayMovingAverage"]
        long_MA = data1["200DayMovingAverage"]
    else:
        revenue = None
        market_cap = None
        gross_profit = None

    financial_metrics = {
        "revenue": revenue,
        "market_cap": market_cap,
        "gross_profit": gross_profit,
        "financial_year": financial_year,
        "description": description,
        "year_week_high": year_week_high,
        "year_week_low": year_week_low,
        "short_MA": short_MA,
        "long_MA": long_MA
    }

    return financial_metrics


def get_sentiment_label(sentiment_score):
    if sentiment_score <= -0.35:
        return "Bearish"
    elif -0.35 < sentiment_score <= -0.15:
        return "Somewhat-Bearish"
    elif -0.15 < sentiment_score < 0.15:
        return "Neutral"
    elif 0.15 <= sentiment_score < 0.35:
        return "Somewhat-Bullish"
    else:
        return "Bullish"


def get_sentiment(stock_symbol):
    api_url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&symbol={stock_symbol}" \
              f"&apikey={ALPHA_VANTAGE_API_KEY}&datatype=json"

    total_sentiment_score = 0
    num_articles = 0

    response = requests.get(api_url)
    if response.status_code == 200:
        try:
            feeds = response.json()["feed"]
            for feed in feeds:
                ticker_sentiments = feed['ticker_sentiment']
                for ticker_sentiment in ticker_sentiments:
                    if ticker_sentiment['ticker'] == stock_symbol:
                        total_sentiment_score += float(ticker_sentiment['ticker_sentiment_score'])
                        num_articles += 1

            average_sentiment_score = total_sentiment_score / num_articles if num_articles else 0
            sentiment_label = get_sentiment_label(average_sentiment_score)
        except KeyError:
            print('KeyError: the "feed" key was not found in the response.')
            sentiment_label = 'Unknown'
    else:
        sentiment_label = 'Unknown'
    return sentiment_label



def generate_stock_chart(data, stock_symbol):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(x=data.index,
                                 open=data['1. open'],
                                 high=data['2. high'],
                                 low=data['3. low'],
                                 close=data['4. close'],
                                 name='Candlestick'))

    fig.update_layout(
        title=f"{stock_symbol} Stock Chart",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        font=dict(
            family="Arial",
            size=14,
            color="black"
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')

    return fig.to_json()

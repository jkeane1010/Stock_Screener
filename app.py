from flask import Flask, render_template, request, session
from math import ceil
from stock_data import *
import re

app = Flask(__name__)

app.secret_key = 'your_secret_key_here'


def get_stock_articles(stock_symbol, page, per_page):
    API_KEY = "53d51dc3de0745338231808a7547d65c"
    newsapi_url = f"https://newsapi.org/v2/everything?q={stock_symbol}&apiKey={API_KEY}&pageSize={per_page}&page={page}"

    response = requests.get(newsapi_url)
    data = response.json()

    if "articles" in data:
        articles = data["articles"]
        total = data["totalResults"]
    else:
        articles = []
        total = 0

    filtered_articles = []
    for article in articles:
        if re.match(r'^[a-zA-Z]', article['title']):
            filtered_articles.append(article)

    return filtered_articles, total


@app.template_filter('format_number')
def format_number(value):
    try:
        value = float(value)
        return "${:,.0f}".format(value)
    except (ValueError, TypeError):
        return value


@app.template_filter('format_price')
def format_number(value):
    try:
        value = float(value)
        return "${:,.2f}".format(value)
    except (ValueError, TypeError):
        return value


@app.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10

    if request.method == 'POST':
        session['stock_symbol'] = request.form.get('stock_symbol')

    # Clear previous session data
    session.pop('data', None)
    session.pop('financial_metrics', None)

    stock_symbol = session.get('stock_symbol', None)
    filtered_articles, total = get_stock_articles(stock_symbol, page, per_page)
    pagination = {
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": ceil(total / per_page),
    }

    if stock_symbol:
        data, last_close_price = fetch_stock_data(stock_symbol)
        financial_metrics = get_company_financials(stock_symbol)
        revenue = financial_metrics.get('revenue')
        market_cap = financial_metrics.get('market_cap')
        gross_profit = financial_metrics.get('gross_profit')
        financial_year = financial_metrics.get('financial_year')
        description = financial_metrics.get('description')
        year_week_high = financial_metrics.get('year_week_high')
        year_week_low = financial_metrics.get('year_week_low')
        short_MA = financial_metrics.get('short_MA')
        long_MA = financial_metrics.get('long_MA')
        sentiment = get_sentiment(stock_symbol)
        if data is not None:
            chart = generate_stock_chart(data, stock_symbol.upper())

        else:
            chart = None
    else:
        chart = None
        revenue = None
        market_cap = None
        gross_profit = None
        financial_year = None
        description = None
        year_week_high = None
        year_week_low = None
        short_MA = None
        long_MA = None
        last_close_price = None
        sentiment = None

    return render_template('index.html', articles=filtered_articles, stock_symbol=stock_symbol, pagination=pagination,
                           chart=chart, revenue=revenue, market_cap=market_cap, gross_profit=gross_profit,
                           financial_year=financial_year, description=description, last_close_price=last_close_price,
                           year_week_high=year_week_high, year_week_low=year_week_low, short_MA=short_MA,
                           long_MA=long_MA, sentiment=sentiment)


if __name__ == '__main__':
    app.run(debug=True)

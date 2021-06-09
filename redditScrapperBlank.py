import re
import praw
import matplotlib.pyplot as plt
import yfinance as yf
from collections import Counter

#############
enter_user_info_here = praw.Reddit(client_id='',
                                   client_secret='',
                                   user_agent='',
                                   username='',
                                   password='')
#############

class Ticker:

    def __init__(self, ticker, count):
        self.ticker = ticker
        self.count = count

    def change(self):
        self.count = self.count + 1

    def __str__(self):
        return "\nThe ticker {} was mentioned {} times on r/SPACs".format(self.ticker, self.count)


def get_top_stock_graph(tic_list):
    data = yf.download(tic_list, '2018-12-1')['Adj Close']

    # plot closing prices
    ((data.pct_change() + 1).cumprod()).plot(figsize=(10, 7))
    plt.legend()
    plt.title("Performance of Most Mentioned Stocks in r/SPACs", fontsize=16)
    plt.ylabel('Cumulative Returns', fontsize=14)
    plt.xlabel("Time", fontsize=14)

    plt.grid(which="major", color='k', linestyle="-.", linewidth=0.5)

    plt.show()


def extract_ticker(text, start):
    # given a starting point in a string of text, this will extract the ticker
    # returns None if it is incorrect

    char_count_in_tic = 0
    ticker = ""

    for char in text[start:]:
        if not char.isalpha():
            if char_count_in_tic == 0:
                return None
            return ticker.upper()
        else:
            ticker += char
            char_count_in_tic += 1

    return ticker.upper()


def search(ticker_list, tic_tac, text):
    blacklist = [
        "YOLO", "IPOD", "YOU", "FYI", "DD", "TO", "THE", "MOON", "WSB", "CNBC", "IPO", "SEC", "OPEN",
        "STOCK", "US", "UK", "BUY", "PIPE", "FDA", "NOW", "UP", "CEO", "TODAY", "BACK", "GRID", "NYSE",
        "PSA", "COVID", "IN", "AS", "OF", "AT", "WHY", "HELP", "OMG", "NASA", "VS", "SPAC", "SPACS",
        "LLC", "CORP", "WTF", "TESLA", "MARS", "TRADE"
    ]

    # checks for $ formatted text
    if '$' in text:
        index = text.find('$') + 1
        word = extract_ticker(text, index)

        if word and word not in blacklist:
            tic_tac.append(word)

            if word not in ticker_list:
                ticker_list.append(word)

    # checks for non-$ formatted text
    word_list = re.sub("[^\w]", " ", text).split()
    for count, word in enumerate(word_list):
        # initial screening of words
        if word.isupper() and len(word) != 1 and (word.upper() not in blacklist) and len(word) <= 5 and word.isalpha():
            tic_tac.append(word)

            if word not in ticker_list:
                ticker_list.append(word)

    return


def run():
    top_tic = []
    ticker_list = []
    tic_tac = []

    reddit = enter_user_info_here

    subreddit = reddit.subreddit('SPACs')
    new_posts = subreddit.new(limit=1000)

    for count, post in enumerate(new_posts):
        search(ticker_list, tic_tac, post.title)

        if (count + 1) % 100 == 0:
            print("\nTotal posts searched: " + str(count + 1) + "\nTotal ticker mentions: " + str(len(tic_tac)) +
                  "\nTotal unique tickers mentions: " + str(len(ticker_list)))

    # determines the most referenced tickers
    data = Counter(tic_tac)
    for i in range(5):
        top_tic.append(data.most_common()[i][0])
    print("The top 5 most mentioned Tickers:", top_tic)

    ticker_class = []
    for ticker in range(len(data.most_common())):
        if (data.most_common()[ticker][1]) > 4:
            ticker_class.append(Ticker(data.most_common()[ticker][0], data.most_common()[ticker][1]))

    for ticker in ticker_class:
        print(ticker)

    # plots the chart of the most referenced tickers
    print("\n")
    get_top_stock_graph(top_tic)


run()

import requests, json, time
from alpaca_trade_api.rest import REST
import scrapy
import csv

CURRENT_TIME = time.strftime("%H:%M:%S", time.localtime())
BASE_URL = "https://paper-api.alpaca.markets"
API_URL = "https://api-inference.huggingface.co/models/ProsusAI/finbert"
DATA_URL = "https://data.alpaca.markets/v2"
ACCOUNT_URL = "https://paper-api.alpaca.markets/v2/account"
ORDERS_URL = "https://paper-api.alpaca.markets/v2/orders"
with open("config.json", "r") as details:
    data = json.load(details)
KEY= data['KEY']
SECRET = data['SECRET']
INFO = {'APCA-API-KEY-ID': KEY,'APCA-API-SECRET-KEY': SECRET}

api = REST(key_id=KEY, secret_key=SECRET, base_url=BASE_URL)

def  getAccount():
    r= requests.get(ACCOUNT_URL, headers=INFO)
    return json.loads(r.content)

def order(symbol, qty, side, type, time_in_force):
    data = {
        "symbol": symbol,
        "qty": qty,
        "side": side,
        "type": type,
        "time_in_force": time_in_force
    }
    r = requests.post(ORDERS_URL, json=data, headers=INFO)
    return json.loads(r.content)

# response = order("AAPL", 100, "buy", "market", "gtc")
headers = {"Authorization": f"Bearer {data['API_KEY']}"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()

stock_list = [
    'AAPL',
]
pos_avg =0
neg_avg =0
neu_avg =0
decesion= "N/A"
articles = []
with open('articles.csv', mode="r") as csv_file: 
    reader = csv.reader(csv_file) 
    #format: (Name, Date, Decision)
    data = list(reader)
articles = data
for i in range(len(stock_list)):
    length = len(api.get_news(stock_list[i]))
    for news in range(length):
        positive = 0
        negative = 0
        neutral = 0
        analysis = query({"inputs":api.get_news(stock_list[i])[news].headline})
        print(analysis)
        for index in range(len(analysis)):
            if(analysis[0][index]['label'] == 'positive'):
                 positive += analysis[0][index]['score']
            elif(analysis[0][index]['label'] == 'negative'):
                negative += analysis[0][index]['score']
            else:
                neutral += analysis[0][index]['score']
        headline = api.get_news(stock_list[i])[news].headline
        print(headline)
        if(positive> negative):
            print("buy")
            decesion = "buy"
            order(stock_list[i], 5, "buy", "market", "gtc")
            
        elif(negative> positive):
            print("short-sell")
            decesion = "short-sell"
            order(stock_list[i], 5, "sell", "market", "gtc")
        print("end")
        articles.append([headline,decesion])
        time.sleep(2)

    # find out the largest one between pos_avg, neg_avg, neu_avg
    # if pos_avg is the largest one, buy the stock
    # if neg_avg is the largest one, short-sell the stock
    # if neu_avg is the largest one, do nothing

with open('articles.csv', mode="w", newline='') as csv_file: #"r" represents the read mode
            writer = csv.writer(csv_file)
            #format: (Name, Date, Decision)
            # write to multiple rows in one statement
            writer.writerows(articles)
            csv_file.close()
'''
with open('stocklist.csv', mode="r") as csv_file: #"r" represents the read mode
    reader = csv.reader(csv_file) #this is the reader object  
    
with open('stocklist.csv', mode="w"):
    reader[INDEXOFSTOCKTOBUY] += THEAMOUNTOFSTOCKS

for item in reader:
    # you have to loop through the document to get each data
    print(item)
'''

with open('articles.csv', mode="r") as csv_file: #"r" represents the read mode
    reader = csv.reader(csv_file) #this is the reader object  
    #format: (Name, Date, Decision)
    data = list(reader)

print(data)
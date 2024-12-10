import requests, json, time
from alpaca_trade_api.rest import REST
import math
import csv

CURRENT_TIME = time.strftime("%H:%M:%S", time.localtime())
BASE_URL = "https://paper-api.alpaca.markets"
API_URL = "https://api-inference.huggingface.co/models/ProsusAI/finbert"
DATA_URL = "https://data.alpaca.markets/v2"
ACCOUNT_URL = "https://paper-api.alpaca.markets/v2/account"
ORDERS_URL = "https://paper-api.alpaca.markets/v2/orders"

with open('config.json', mode='r') as file:
    INFO = json.load(file)
# INFO = {'APCA-API-KEY-ID': KEY,'APCA-API-SECRET-KEY': SECRET}
MAX_SAFE_BUYING_POWER = 100000
RISK_SCALING_FACTOR = 3.5
def  getAccount():
    r= requests.get(ACCOUNT_URL, headers=INFO)
    return json.loads(r.content)
bp = float(getAccount()['buying_power'])
normalized_power = min(bp / MAX_SAFE_BUYING_POWER, 1)
# Calculated with sigmoid
RISK = 1 / (1 + math.exp(-RISK_SCALING_FACTOR * (normalized_power - 0.5)))

BASE_QTY = 20

api = REST(key_id=INFO["APCA-API-KEY-ID"], secret_key=INFO["APCA-API-SECRET-KEY"], base_url=BASE_URL)


def order(symbol, side, type, time_in_force):
    data = {
        "symbol": symbol,
        "qty": BASE_QTY*RISK,
        "side": side,
        "type": type,
        "time_in_force": time_in_force
    }
    r = requests.post(ORDERS_URL, json=data, headers=INFO)
    return json.loads(r.content)

# response = order("AAPL", 100, "buy", "market", "gtc")
headers = {"Authorization": f"Bearer {'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'}"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
    
	return response.json()

stock_list = [
    'AAPL',
    'GOOGL',
]
pos_avg =0
neg_avg =0
neu_avg =0
decesion= "N/A"
articles = []
#format: (Name, Date, Decision)

for i in range(len(stock_list)):
    GetNews = api.get_news(stock_list[i])
    for news in range(len(GetNews)):
        positive = 0
        negative = 0
        neutral = 0
        print(GetNews[news])
        with open('stockDecisions.csv', mode="r") as csv_file: #"r" represents the read mode
            reader = csv.reader(csv_file) #this is the reader object  
            #format: (Name, Date, Decision)
            Checkdata = list(reader)
        if ((any(sublist[0] == GetNews[news].headline for sublist in Checkdata) == False)):
            print('**'*100)
            analysis = query({"inputs":GetNews[news].headline})
            print(analysis)
            for index in range(len(analysis)):
                if(analysis[0][index]['label'] == 'positive'):
                     positive += analysis[0][index]['score']
                
                elif(analysis[0][index]['label'] == 'negative'):
                    negative += analysis[0][index]['score']
                else:
                    neutral += analysis[0][index]['score']
            headline = GetNews[news].headline
            print(headline)
            if((neutral>negative) & (neutral>positive)):
                neu_avg += 1
            else:
                if(positive> negative):
                    print("buy")
                    decesion = "buy"
                    pos_avg += 1
                elif(negative> positive):
                    print("short-sell")
                    decesion = "short-sell"
                    neg_avg += 1
            articles.append([headline,decesion,BASE_QTY*RISK])
        print("end")
        time.sleep(2)
    if ((neu_avg>pos_avg) & (neu_avg>neg_avg)):
        print('-'*100)
        print("skip: "+stock_list[i])
    else:
        if (pos_avg>neg_avg):
            print('-'*100)
            print("real-Buy"+stock_list[i])
            decision = "buy"
            order(stock_list[i], "buy", "market", "gtc")
        if (neg_avg>pos_avg):
            print('-'*100)
            print("real-Sell: "+stock_list[i])
            decision = "sell"
            order(stock_list[i], "sell", "market", "gtc")
        


with open('articles.csv', mode="w", newline='') as csv_file: 
            writer = csv.writer(csv_file)
            #format: (Name, Decision, Date)
            # write to multiple rows in one statement
            writer.writerows(articles)
            csv_file.close()

with open('stockDecisions.csv', mode="a", newline='') as stock_decisions_file: 
            stock_decisions_writer = csv.writer(stock_decisions_file)
          
            for article in articles:
                stock_decisions_writer.writerow([article[0], article[1], article[2]])
 
'''
with open('stocklist.csv', mode="r") as csv_file: 
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

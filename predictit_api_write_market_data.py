# Import modules
import json
import requests
import pandas as pd

# Pull in market data from PredictIt's API
URL = "https://www.predictit.org/api/marketdata/all/"
response = requests.get(URL)
jsondata = response.json()

# Replace null values with zero
def dict_clean(items):
    result = {}
    for key, value in items:
        if value is None:
            value = 0
        result[key] = value
    return result
dict_str = json.dumps(jsondata)
jsondata = json.loads(dict_str, object_pairs_hook=dict_clean)

# Market data by contract/price in dataframe
data = []
for p in jsondata['markets']:
	for k in p['contracts']:
		data.append([p['id'],p['name'],p['url'],k['id'],k['name'],k['bestBuyYesCost'],k['bestBuyNoCost'],k['bestSellYesCost'],k['bestSellNoCost'],p['timeStamp'],p['status']])

# Pandas dataframe named 'df'
df = pd.DataFrame(data)

# Update dataframe column names
df.columns=['Market_ID','Market_Name','Market_URL','Contract_ID','Contract_Name','bestBuyYesCost','bestBuyNoCost','BestSellYesCost','BestSellNoCost','Time_Stamp','Status']

# Write dataframe to CSV file in working directory
df.to_csv(r'./predictit_all_markets.csv', sep=',', encoding='utf-8', header='true')
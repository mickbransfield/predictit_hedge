# Import modules
import json
import requests
import pandas as pd

# Pull in market data from PredictIt's API
URL = "https://www.predictit.org/api/marketdata/all/"
response = requests.get(URL)
jsondata = response.json()

# Remove null values from data
def dict_clean(items):
    result = {}
    for key, value in items:
        if value is None:
            value = 0
        result[key] = value
    return result

dict_str = json.dumps(jsondata)
jsondata = json.loads(dict_str, object_pairs_hook=dict_clean)

# Market data by contract and YES/NO price
#for p in jsondata['markets']:
#    #print('Market ID: ' + '%d' % p['id'],",", 'Market Name: ' + p['name'])
#    for k in p['contracts']:
#        print('Market ID: ' + '%d' % p['id'],",", 'Market Name: ' + p['name'],",",'Contract ID: ' + '%d' % k['id'],",", 'Contract Name: ' + k['name'],",",'Yes Price: ' + '%4.2f' % k['bestBuyYesCost'],",",'No Price: ' + '%4.2f' % k['bestBuyNoCost']) 


# Market data by contract/price in dataframe
data = []
for p in jsondata['markets']:
	for k in p['contracts']:
		data.append([p['id'],p['name'],p['status'],k['id'],k['name'],k['bestBuyYesCost'],k['bestBuyNoCost']])

# Pandas dataframe named 'df'
df = pd.DataFrame(data)

# Update dataframe column names
df.columns=['Market ID','Market Name','Market Status','Contract ID','Contract Name','Yes Price','No Price']

# Add columns to identify correlated markets
df['Trump Wins'] = 0
df['Biden Wins'] = 0

# Print dataframe
print(df)

# Write dataframe to CSV file in working directory
df.to_csv(r'./predictit_markets.csv', sep=',', encoding='utf-8', header='true')

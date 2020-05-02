# import modules
import json
import requests
import pandas as pd

# pull in market data from PredictIt's API
URL = "https://www.predictit.org/api/marketdata/all/"
response = requests.get(URL)
jsondata = json.loads(response.text)

# print individual market to see data available
print(jsondata['markets'][0])

# pull market IDs
id = []
for i in jsondata['markets']:
	id.append(i.get('id'))

# pul market names
name = []
for n in jsondata['markets']:
	name.append(n.get('name'))

# print contract to see data available
print(jsondata['markets'][0]['contracts'])

# Merge IDs and names into one dictionary
predictit_markets = dict(zip(id, name))

# Convert dictionary into dataframe
predictit_markets = pd.DataFrame.from_dict(predictit_markets, orient='index', columns=['Market Name'])
predictit_markets['Trump Wins'] = 0
predictit_markets['Biden Wins'] = 0
print(predictit_markets)
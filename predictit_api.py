# import modules
import json
import requests
import pandas as pd

# pull in market data from PredictIt's API
URL = "https://www.predictit.org/api/marketdata/all/"
response = requests.get(URL)
jsondata = response.json()

# find data type (dictionary)
#print(type(jsondata))

# print individual market to see data available
#print(jsondata['markets'][10])

# pull market IDs
id = []
for i in jsondata['markets']:
	id.append(i.get('id'))

# pul market names
name = []
for n in jsondata['markets']:
	name.append(n.get('name'))

# print contract to see data available
#print(jsondata['markets'][0]['contracts'])

# Merge IDs and names into one dictionary
#predictit_markets = dict(zip(id, name))

# Convert dictionary into dataframe
#predictit_markets = pd.DataFrame.from_dict(predictit_markets, orient='index', columns=['Market Name'])
#predictit_markets['Trump Wins'] = 0
#predictit_markets['Biden Wins'] = 0
#print(predictit_markets)

#Remove null values from data
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
		data.append([p['id'],p['name'],k['id'],k['name'],k['bestBuyYesCost'],k['bestBuyNoCost']])

df = pd.DataFrame(data)
df.columns=['Market ID','Market Name','Contract ID','Contract Name','Yes Price','No Price']
df['Trump Wins'] = 0
df['Biden Wins'] = 0
print(df)

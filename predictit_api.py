# Import modules
import json
import requests
import pandas as pd
import numpy as np
import random

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

# Market data by contract/price in dataframe
data = []
for p in jsondata['markets']:
	for k in p['contracts']:
		data.append([p['id'],p['name'],k['id'],k['name'],k['bestBuyYesCost'],k['bestBuyNoCost']])

# Pandas dataframe named 'df'
df = pd.DataFrame(data)

# Update dataframe column names
df.columns=['Market_ID','Market_Name','Contract_ID','Contract_Name','Yes_Price','No_Price']

# Write dataframe to CSV file in working directory
df.to_csv(r'./predictit_all_markets.csv', sep=',', encoding='utf-8', header='true')

# Add columns to identify correlated markets
df['Trump_Wins'] = 0
df['Biden_Wins'] = 0

# Market 2721 Which party will win the 2020 U.S. presidential election? Contract 4389 Republican
# Market 3698 Who will win the 2020 U.S. presidential election? Contract 7943 Donald Trump
trump = (df['Contract_ID']==4389) | (df['Contract_ID']==7943) 
df['Trump_Wins'] = np.where(trump,1,0)

# Market 2721 Which party will win the 2020 U.S. presidential election? Contract 4390 Democratic
# Market 3698 Who will win the 2020 U.S. presidential election? Contract 7940 Joe Biden
# Market 5960 Will the 2020 SC Democratic primary winner win the presidency? Contract 18036 Will the 2020 SC Democratic primary winner win the presidency?
# Market 5963 Will the 2020 MA Democratic primary winner win the presidency? Contract 18039 Will the 2020 MA Democratic primary winner win the presidency?
biden = (df['Contract_ID']==4390) | (df['Contract_ID']==7940) | (df['Contract_ID']==18036) | (df['Contract_ID']==18039) 
df['Biden_Wins'] = np.where(biden,1,0)

# Filter dataframe to correlated markets
Trump_Contracts = df.loc[df['Trump_Wins'] == 1]
Biden_Contracts = df.loc[df['Biden_Wins'] == 1]

# Cost-Benefit
Trump_Contracts['Trump_Win_Gross'] = 1- Trump_Contracts['Yes_Price']
Trump_Contracts['Fees'] = 0.10 * Trump_Contracts['Trump_Win_Gross']
Trump_Contracts['Trump_Win_Profit'] = Trump_Contracts['Trump_Win_Gross']-Trump_Contracts['Fees']
Trump_Contracts['Trump_Loss'] = Trump_Contracts['Yes_Price']

Biden_Contracts['Biden_Win_Gross'] = 1- Biden_Contracts['Yes_Price']
Biden_Contracts['Fees'] = 0.10 * Biden_Contracts['Biden_Win_Gross']
Biden_Contracts['Biden_Win_Profit'] = Biden_Contracts['Biden_Win_Gross']-Biden_Contracts['Fees']
Biden_Contracts['Biden_Loss'] = Biden_Contracts['Yes_Price']

# Round to 2 decimal places
#Biden_Contracts['Fees']=Biden_Contracts['Fees'].apply(lambda x:round(x,2))
#Biden_Contracts['Biden_Win_Profit']=Biden_Contracts['Biden_Win_Profit'].apply(lambda x:round(x,2))

# Print dataframes
print(Trump_Contracts)
print(Biden_Contracts)

BL = np.array([Biden_Contracts['Biden_Loss']])
TW = np.array([Trump_Contracts['Trump_Win_Profit']])
print(BL, type(BL))
print(TW, type(TW))

#d = []
#for t in Trump_Contracts['Trump_Win_Profit']:
#		Trump_Contracts['Trump_Win_Profit'] + Biden_Contracts['Biden_Loss']
#x = pd.DataFrame(d)	
#print(x)
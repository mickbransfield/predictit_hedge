# Import modules
import json
import requests
import pandas as pd
pd.options.mode.chained_assignment = None #hide SettingWithCopyWarning
pd.set_option('display.max_columns', None) # Set it to None to display all columns in the dataframe
pd.set_option('display.max_colwidth', None) #  print contents of that column without truncated
pd.set_option('display.width', None) # Width of the display in characters.

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
		data.append([p['id'],p['name'],k['id'],k['name'],k['bestBuyYesCost'],k['bestBuyNoCost'],k['bestSellYesCost'],k['bestSellNoCost']])

# Pandas dataframe named 'df'
df = pd.DataFrame(data)

# Update dataframe column names
df.columns=['Market_ID','Market_Name','Contract_ID','Contract_Name','bestBuyYesCost','bestBuyNoCost','BestSellYesCost','BestSellNoCost']

# Filter dataframe to list of markets with only 2 contracts
df1 = df.groupby('Market_Name')['Market_ID'].value_counts().reset_index(name ='contract_counts')
df1 = df1.loc[df1['contract_counts'] == 2]
Markets_Dual_contracts_list = df1['Market_ID'].tolist()
Markets_Dual_contracts_df = df[df['Market_ID'].isin(Markets_Dual_contracts_list)]
print(Markets_Dual_contracts_df)
# Find inefficiencies in Buy Yes and Buy No prices of inversely correlated contracts
Markets_Dual_contracts_df['interval_AYes_BNo'] = (Markets_Dual_contracts_df.groupby('Market_ID').apply(lambda x: x.bestBuyYesCost-x.bestBuyNoCost.shift(1))).values
Markets_Dual_contracts_df['interval_ANo_BYes'] = (Markets_Dual_contracts_df.groupby('Market_ID').apply(lambda x: x.bestBuyNoCost-x.bestBuyYesCost.shift(1))).values
print(Markets_Dual_contracts_df['interval_AYes_BNo'])
print(Markets_Dual_contracts_df['interval_ANo_BYes'])
# Remove alternating NaN rows
Markets_Dual_contracts_df = Markets_Dual_contracts_df.dropna(subset=['interval_AYes_BNo'])

# Remove Markets with no delta in Buy Yes and Buy No prices
Markets_Dual_contracts_df = Markets_Dual_contracts_df.loc[(Markets_Dual_contracts_df['interval_AYes_BNo'] != 0) & (Markets_Dual_contracts_df['interval_ANo_BYes'] != 0)]

# Drop extraneous columns
Markets_Dual_contracts_df = Markets_Dual_contracts_df.drop(['Contract_ID', 'Contract_Name','bestBuyYesCost','bestBuyNoCost','BestSellYesCost', 'BestSellNoCost'], axis=1)

# Sort by absolute value
Markets_Dual_contracts_df = Markets_Dual_contracts_df.reindex(Markets_Dual_contracts_df.interval_AYes_BNo.abs().sort_values(ascending=False).index)

print("Below are markets with price discrepancies in two inversely correlated contracts. For example, either a Republican or Democrat presidential candidate will win the state of Idaho, but there might be different buy prices for Republican Yes and Democrat No, and vice versa.\n\n") 
print(Markets_Dual_contracts_df)
# Import modules
import json
import requests
import pandas as pd
pd.options.mode.chained_assignment = None #hide SettingWithCopyWarning
pd.set_option('display.max_columns', None) # Set it to None to display all columns in the dataframe
pd.set_option('display.max_colwidth', -1) #  print contents of that column without truncated
pd.set_option('display.width', None) # Width of the display in characters.
import numpy as np

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
		data.append([p['id'],p['name'],k['id'],k['name'],k['bestBuyYesCost'],k['bestBuyNoCost']])

# Pandas dataframe named 'df'
df = pd.DataFrame(data)

# Update dataframe column names
df.columns=['Market_ID','Market_Name','Contract_ID','Contract_Name','Yes_Price','No_Price']

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
Trump_Contracts_Yes = df.loc[df['Trump_Wins'] == 1]
Biden_Contracts_Yes = df.loc[df['Biden_Wins'] == 1]

Trump_Contracts_No = df.loc[df['Trump_Wins'] == 1]
Biden_Contracts_No = df.loc[df['Biden_Wins'] == 1]

# Create new column of Market/Contract names
Trump_Contracts_Yes['market_contract'] = Trump_Contracts_Yes['Market_Name'] +': '+ Trump_Contracts_Yes['Contract_Name'] +': Yes'
Biden_Contracts_Yes['market_contract'] = Biden_Contracts_Yes['Market_Name'] +': '+ Biden_Contracts_Yes['Contract_Name'] +': Yes'

Trump_Contracts_No['market_contract'] = Trump_Contracts_No['Market_Name'] +': '+ Trump_Contracts_No['Contract_Name'] +': No'
Biden_Contracts_No['market_contract'] = Biden_Contracts_No['Market_Name'] +': '+ Biden_Contracts_No['Contract_Name'] +': No'

# Cost-Benefit Trump YES contracts
Trump_Contracts_Yes['Trump_Win_Gross'] = 1 - Trump_Contracts_Yes['Yes_Price']
Trump_Contracts_Yes['Fees'] = 0.10 * Trump_Contracts_Yes['Trump_Win_Gross']
Trump_Contracts_Yes['Trump_Win_Profit'] = Trump_Contracts_Yes['Trump_Win_Gross']-Trump_Contracts_Yes['Fees']
Trump_Contracts_Yes['Trump_Loss'] = Trump_Contracts_Yes['Yes_Price']

# Cost-Benefit Biden NO contracts
Biden_Contracts_No['Trump_Win_Gross'] = 1 - Biden_Contracts_No['No_Price']
Biden_Contracts_No['Fees'] = 0.10 * Biden_Contracts_No['Trump_Win_Gross']
Biden_Contracts_No['Trump_Win_Profit'] = Biden_Contracts_No['Trump_Win_Gross']-Biden_Contracts_No['Fees']
Biden_Contracts_No['Trump_Loss'] = Biden_Contracts_No['No_Price']

# Cost-Benefit Biden YES contracts
Biden_Contracts_Yes['Biden_Win_Gross'] = 1 - Biden_Contracts_Yes['Yes_Price']
Biden_Contracts_Yes['Fees'] = 0.10 * Biden_Contracts_Yes['Biden_Win_Gross']
Biden_Contracts_Yes['Biden_Win_Profit'] = Biden_Contracts_Yes['Biden_Win_Gross']-Biden_Contracts_Yes['Fees']
Biden_Contracts_Yes['Biden_Loss'] = Biden_Contracts_Yes['Yes_Price']

# Cost-Benefit Trump NO contracts
Trump_Contracts_No['Biden_Win_Gross'] = 1 - Trump_Contracts_No['No_Price']
Trump_Contracts_No['Fees'] = 0.10 * Trump_Contracts_No['Biden_Win_Gross']
Trump_Contracts_No['Biden_Win_Profit'] = Trump_Contracts_No['Biden_Win_Gross']-Trump_Contracts_No['Fees']
Trump_Contracts_No['Biden_Loss'] = Trump_Contracts_No['No_Price']

# Concatenate Trump Yes & Biden No
Trump_Contracts = pd.concat([Trump_Contracts_Yes, Biden_Contracts_No], axis=0)

# Concatenate Biden Yes & Trump No
Biden_Contracts = pd.concat([Biden_Contracts_Yes, Trump_Contracts_No], axis=0)

# Create a list of net gain/loss for Trump victory & Biden loss
Trump_Victory_Margins=[]
for x, y in [(x,y) for x in Biden_Contracts['Biden_Loss'] for y in Trump_Contracts['Trump_Win_Profit']]:
    Trump_Victory_Margins.append([x, y])
Trump_Victory_Margins = [tup[1]-tup[0] for tup in Trump_Victory_Margins]

# Create a list of net gain/loss for Biden victory & Trump loss
Biden_Victory_Margins=[]
for x, y in [(x,y) for x in Biden_Contracts['Biden_Win_Profit'] for y in Trump_Contracts['Trump_Loss']]:
    Biden_Victory_Margins.append([x, y])
Biden_Victory_Margins = [tup[0]-tup[1] for tup in Biden_Victory_Margins]

# Create list of contract combinations 
Combination_Contracts=[]
for x, y in [(x,y) for x in Biden_Contracts['market_contract'] for y in Trump_Contracts['market_contract']]:
    Combination_Contracts.append([x, y])

Contract_IDs=[]
for x, y in [(x,y) for x in Biden_Contracts['Contract_ID'] for y in Trump_Contracts['Contract_ID']]:
    Contract_IDs.append(x-y)

# Merge lists into dataframe
Results_df = pd.DataFrame(
    {'Trump_Victory_Margins': Trump_Victory_Margins,
	'Biden_Victory_Margins': Biden_Victory_Margins,
	'Combination_Contracts': Combination_Contracts,
	'Contract_IDs': Contract_IDs
    })

# Remove Yes/No contracts since user can't buy Yes and No on same contract
Results_df = Results_df[(Results_df['Contract_IDs'] != 0)]

# Print hedge opportunities if they exist
records = Results_df[(Results_df['Trump_Victory_Margins'] > 0) & (Results_df['Biden_Victory_Margins'] > 0)& (Results_df['Contract_IDs'] != 0)]
if records.empty:
	print("Sorry, no hedge opportunities at moment.")
else:
	print("Hedge opportunity:",)
	for index, row in records.iterrows():
		print(row['Combination_Contracts'])

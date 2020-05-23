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
df['Group_A'] = 0
df['Group_B'] = 0

# Brief user instructions
print("Enter inversely correlated contracts in the prompts. For example, 'Group A' could be contracts of Trump winning the General Election and 'Group B' Biden winning.\n\nIf you use multiple contracts per group, separate with a comma.\n") 

# Add 1 to Group_A column for contracts from user input
# Example: 4389,7943
A = [int(A) for A in input("Enter Group A: ").split(",")]
df['Group_A'] = np.where(df['Contract_ID'].isin(A), 1, 0)

# Add 1 to Group_B column for contracts from user input
# Example: 4390,7940,18036,18039
B = [int(B) for B in input("Enter Group B: ").split(",")]
df['Group_B'] = np.where(df['Contract_ID'].isin(B), 1, 0)

# Filter dataframe to correlated markets
Group_A_Contracts_Yes = df.loc[df['Group_A'] == 1]
Group_B_Contracts_Yes = df.loc[df['Group_B'] == 1]

Group_A_Contracts_No = df.loc[df['Group_A'] == 1]
Group_B_Contracts_No = df.loc[df['Group_B'] == 1]

# Create new column of Market/Contract names
Group_A_Contracts_Yes['market_contract'] = Group_A_Contracts_Yes['Market_Name'] +': '+ Group_A_Contracts_Yes['Contract_Name'] +': Yes'
Group_B_Contracts_Yes['market_contract'] = Group_B_Contracts_Yes['Market_Name'] +': '+ Group_B_Contracts_Yes['Contract_Name'] +': Yes'

Group_A_Contracts_No['market_contract'] = Group_A_Contracts_No['Market_Name'] +': '+ Group_A_Contracts_No['Contract_Name'] +': No'
Group_B_Contracts_No['market_contract'] = Group_B_Contracts_No['Market_Name'] +': '+ Group_B_Contracts_No['Contract_Name'] +': No'

# Cost-Benefit Group A YES contracts
Group_A_Contracts_Yes['Group_A_Win_Gross'] = 1 - Group_A_Contracts_Yes['Yes_Price']
Group_A_Contracts_Yes['Fees'] = 0.10 * Group_A_Contracts_Yes['Group_A_Win_Gross']
Group_A_Contracts_Yes['Group_A_Win_Profit'] = Group_A_Contracts_Yes['Group_A_Win_Gross']-Group_A_Contracts_Yes['Fees']
Group_A_Contracts_Yes['Group_A_Loss'] = Group_A_Contracts_Yes['Yes_Price']

# Cost-Benefit Group B NO contracts
Group_B_Contracts_No['Group_A_Win_Gross'] = 1 - Group_B_Contracts_No['No_Price']
Group_B_Contracts_No['Fees'] = 0.10 * Group_B_Contracts_No['Group_A_Win_Gross']
Group_B_Contracts_No['Group_A_Win_Profit'] = Group_B_Contracts_No['Group_A_Win_Gross']-Group_B_Contracts_No['Fees']
Group_B_Contracts_No['Group_A_Loss'] = Group_B_Contracts_No['No_Price']

# Cost-Benefit Group B YES contracts
Group_B_Contracts_Yes['Group_B_Win_Gross'] = 1 - Group_B_Contracts_Yes['Yes_Price']
Group_B_Contracts_Yes['Fees'] = 0.10 * Group_B_Contracts_Yes['Group_B_Win_Gross']
Group_B_Contracts_Yes['Group_B_Win_Profit'] = Group_B_Contracts_Yes['Group_B_Win_Gross']-Group_B_Contracts_Yes['Fees']
Group_B_Contracts_Yes['Group_B_Loss'] = Group_B_Contracts_Yes['Yes_Price']

# Cost-Benefit Group A NO contracts
Group_A_Contracts_No['Group_B_Win_Gross'] = 1 - Group_A_Contracts_No['No_Price']
Group_A_Contracts_No['Fees'] = 0.10 * Group_A_Contracts_No['Group_B_Win_Gross']
Group_A_Contracts_No['Group_B_Win_Profit'] = Group_A_Contracts_No['Group_B_Win_Gross']-Group_A_Contracts_No['Fees']
Group_A_Contracts_No['Group_B_Loss'] = Group_A_Contracts_No['No_Price']

# Concatenate A Yes & B No
Group_A_Contracts = pd.concat([Group_A_Contracts_Yes, Group_B_Contracts_No], axis=0)

# Concatenate B Yes & A No
Group_B_Contracts = pd.concat([Group_B_Contracts_Yes, Group_A_Contracts_No], axis=0)

# Create a list of net gain/loss for A victory & B loss
Group_A_Victory_Margins=[]
for x, y in [(x,y) for x in Group_B_Contracts['Group_B_Loss'] for y in Group_A_Contracts['Group_A_Win_Profit']]:
    Group_A_Victory_Margins.append([x, y])
Group_A_Victory_Margins = [tup[1]-tup[0] for tup in Group_A_Victory_Margins]

# Create a list of net gain/loss for B victory & A loss
Group_B_Victory_Margins=[]
for x, y in [(x,y) for x in Group_B_Contracts['Group_B_Win_Profit'] for y in Group_A_Contracts['Group_A_Loss']]:
    Group_B_Victory_Margins.append([x, y])
Group_B_Victory_Margins = [tup[0]-tup[1] for tup in Group_B_Victory_Margins]

# Create list of contract combinations 
Combination_Contracts=[]
for x, y in [(x,y) for x in Group_B_Contracts['market_contract'] for y in Group_A_Contracts['market_contract']]:
    Combination_Contracts.append([x, y])

Contract_IDs=[]
for x, y in [(x,y) for x in Group_B_Contracts['Contract_ID'] for y in Group_A_Contracts['Contract_ID']]:
    Contract_IDs.append(x-y)

# Merge lists into dataframe
Results_df = pd.DataFrame(
    {'Group_A_Victory_Margins': Group_A_Victory_Margins,
	'Group_B_Victory_Margins': Group_B_Victory_Margins,
	'Combination_Contracts': Combination_Contracts,
	'Contract_IDs': Contract_IDs
    })

# Remove Yes/No contracts since user can't buy Yes and No on same contract
Results_df = Results_df[(Results_df['Contract_IDs'] != 0)]

# Print hedge opportunities if they exist
records = Results_df[(Results_df['Group_A_Victory_Margins'] > 0) & (Results_df['Group_B_Victory_Margins'] > 0)& (Results_df['Contract_IDs'] != 0)]

if records.empty:
	print("Sorry, no opportunities at moment for pairs trading in the contracts you selected.")
else:
	print("Pairs trading opportunity:",)
	for index, row in records.iterrows():
		print(row['Combination_Contracts'])

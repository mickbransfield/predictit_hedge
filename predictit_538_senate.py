# Import modules
import json
import requests
import pandas as pd
pd.options.mode.chained_assignment = None #hide SettingWithCopyWarning
pd.set_option('display.max_columns', None) # Set it to None to display all columns in the dataframe
pd.set_option('display.max_colwidth', None) #  print contents of that column without truncated
pd.set_option('display.width', None) # Width of the display in characters.



senate_candidates = [[6272, 'Greenfield', 22293], 
					[6272, 'Ernst', 22292], 
					[6284, 'Cunningham', 17017],
					[6284, 'Tillis', 17016],
					[6280, 'Peters', 22041],
					[6280, 'James', 22040],
					[6268, 'Kelly', 17019],
					[6268, 'McSally', 17018],
					[6292, 'Harrison', 22700],
					[6292, 'Graham', 22699],   
					[6279, 'Collins', 17022],
					[6279, 'Gideon', 17023],
					[6269, 'Hickenlooper', 17021],
					[6269, 'Gardner', 17020],
					[6283, 'Bullock', 22014],
					[6283, 'Daines', 22013]] 
  
# Create the pandas DataFrame key
df = pd.DataFrame(senate_candidates, columns = ['race_id', 'answer', 'Contract_ID'])

# Pull in market data from PredictIt's API
Predictit_URL = "https://www.predictit.org/api/marketdata/all/"
Predictit_response = requests.get(Predictit_URL)
jsondata = Predictit_response.json()

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

# Pandas dataframe named 'predictit_df'
predictit_df = pd.DataFrame(data)

# Update dataframe column names
predictit_df.columns=['Market_ID','Market_Name','Contract_ID','Contract_Name','bestBuyYesCost','bestBuyNoCost','BestSellYesCost','BestSellNoCost']

# Pull in polling data from 538's API at https://projects.fivethirtyeight.com/polls-page/senate_polls.csv
senate_polling = pd.read_csv('https://projects.fivethirtyeight.com/polls-page/senate_polls.csv')
senate_polling = senate_polling[senate_polling['election_date'] == '11/3/20']

# Drop extraneous columns
senate_polling = senate_polling.drop(['pollster_id', 'pollster','sponsor_ids','sponsors','display_name', 'pollster_rating_id', 'pollster_rating_name', 'fte_grade', 'sample_size', 'population', 'population_full', 'methodology', 'seat_number', 'seat_name', 'start_date', 'end_date', 'sponsor_candidate', 'internal', 'partisan', 'tracking', 'nationwide_batch', 'ranked_choice_reallocated', 'notes', 'url'], axis=1)

# Filter to most recent poll per candidate
senate_polling['created_at'] = pd.to_datetime(senate_polling['created_at']) #convert 'created_at' to datetime
recent_senate_polling = senate_polling.sort_values(by=['created_at']).drop_duplicates(subset='candidate_name', keep='last')

# Merge key and 538 dataframes together
df = pd.merge(df, recent_senate_polling, on=['race_id', 'answer'])

# Merge key and PredicitIt
df = pd.merge(df, predictit_df, on=['Contract_ID'])
#df['recent_poll-predictit'] = df['pct'] - df['bestBuyYesCost']*100

#print out select columns
print(df[['state', 'office_type', 'answer', 'pct', 'bestBuyYesCost']])

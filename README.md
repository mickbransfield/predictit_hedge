# PredictIt Hedge
### Hedge opportunities on PredictIt due to inefficient pricing in correlated markets

There are situations for hedge betting in different PredictIt markets due to inefficient pricing related to the presidential election.
For example, when Trump winning is priced at $0.50/share and Biden winning is priced at $0.44/share, the opportunity exists to buy an equal number of shares for both candidates and net a profit regardless of who wins.

### Here's the basic math:  
Trump Yes: $0.50  
Biden Yes: $0.44  

Trump wins:  
Gain = $1.00 - $0.50 = $0.50  
Fee = $0.50 * 10% = $0.05  
$0.50(gain) - $0.05(fee) - $0.44(Biden loss) = $0.01  

Biden wins:  
Gain = $1.00 - $0.44 = $0.56  
Fee = $.056 * 10% = $0.056  
$0.56(gain) - $0.056(fee) - $0.50(Trump loss) = $0.004  

### Two separate files:
* [predictit_hedge_2020_presidential.py](https://github.com/mauricebransfield/predictit_hedge/blob/master/predictit_hedge_2020_presidential.py), looks for hedge opportunities in Trump and Biden-related contracts.
* [predictit_api_write_market_data.py](https://github.com/mauricebransfield/predictit_hedge/blob/master/predictit_api_write_market_data.py), simply writes to CSV the current market and contract prices in PredictIt.

### Naturally, there are a few qualifications:
* Similar markets are treated as equals, ie 'Democratic candidate winning presidency' = 'Biden winning presidency.'
* While this code accounts for the 10% fee on gains from trades, it does not factor in the 5% withdrawl fee.
* The specific markets/contracts are hard coded to Yes& No prices of 2 contracts for Trump winning and 4 contracts for Biden winning.

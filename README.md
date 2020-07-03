# PredictIt Hedge
### Hedge opportunities on PredictIt due to inefficient pricing in correlated markets

There are opportunities for pairs trading in PredictIt markets due to inefficient pricing of shares. It is possible to by an equal number of inversely correlated shares and net a profit regardless of who wins.

### Here's an example:  
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

### Five python scripts to help identify opportunities:
* [predictit_hedge_2020_presidential.py](https://github.com/mauricebransfield/predictit_hedge/blob/master/predictit_hedge_2020_presidential.py), looks for hedge opportunities in Trump and Biden-related contracts.
* [predictit_hedge.py](https://github.com/mauricebransfield/predictit_hedge/blob/master/predictit_hedge.py), looks for hedge opportunities in user-inputted contracts.
* [predictit_api_write_market_data.py](https://github.com/mauricebransfield/predictit_hedge/blob/master/predictit_api_write_market_data.py), writes to CSV the current market and contract prices in PredictIt.
* [predictit_dual_contracts.py](https://github.com/mauricebransfield/predictit_hedge/blob/master/predictit_dual_contracts.py), in markets with only 2 contracts looks for discrepancies in Yes/No prices.
* [predictit_538_senate.py](https://github.com/mauricebransfield/predictit_hedge/blob/master/predictit_538_senate.py), compares PredictIt share prices with most recent 538 poll in US Senate races.

### Naturally, there are a few qualifications:
* While the code accounts for the 10% fee on gains from trades, it does not factor in the 5% withdrawal fee.
* In predictit_hedge_2020_presidential.py, similar markets are treated as equals, e.g. 'Democratic candidate winning presidency' = 'Biden winning presidency.'
* In predictit_hedge_2020_presidential.py, contracts are hard coded to Yes & No prices of 2 contracts for Trump winning and 5 contracts for Biden winning.

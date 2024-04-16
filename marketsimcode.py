"""
"""
"""
Student Name: Joshua Varghese
GT User ID: jvarghese42	   		 	   			  		 			     			  	 d
GT ID: 903508453 		
"""

"""
Improved version of marketsim code that accepts a "trades" DataFrame (instead of a file).
"""

# IMPORTS
import pandas as pd
from util import get_data
import numpy as np

# def compute_portvals(trades_df, start_val = 100000, commision = 0.00, impact = 0.00):
#     #trades_df = trades_df.sort_index()
#
#     if trades_df.empty:
#         print("DataFrame is empty!")
#         return pd.DataFrame()
#
#     symbols = trades_df['Symbol'].unique().tolist()
#     #symbol = "JPM"
#
#     start_date = trades_df.index.min()
#     end_date = trades_df.index.max()
#
#     price_data = get_data(symbols, pd.date_range(start_date, end_date), addSPY=True, colname='Adj Close')
#     prices = price_data[symbols]
#     prices['Cash'] = 1.0
#
#     # Initialize a new df for tracking trades
#     trades = pd.DataFrame(index=prices.index, columns=prices.columns)
#     trades.fillna(0.0, inplace=True)
#     trades['Cash'] = start_val
#
#     #process trades
#     for index, row in trades_df.iterrows():
#         symbol = row['Symbol']
#         #order = row['Order']
#         shares = row['Shares']
#         price = prices.loc[index, symbol]
#         trade_impact = prices.at[index, symbol] * shares * impact
#
#         if shares > 0: #order == 'BUY'
#             trades.loc[index, symbol] += shares
#             trades.loc[index, 'Cash'] -= (shares * price) * (1 - impact) + commision
#         elif shares < 0: #order == 'SELL'
#             trades.loc[index, symbol] -= shares
#             trades.loc[index, 'Cash'] += (shares * price) * (1 - impact) - commision
#
#     # Copmpute holdings
#     holdings = trades.cumsum()
#     value = holdings * prices
#     portvals = value.sum(axis = 1)
#
#     return portvals.to_frame("Portfolio Value")
#
# def test_code():
#     # Example DataFrame of trades, replace with your actual DataFrame from TOS or other source
#     trades_example = pd.DataFrame({
#         'Symbol': ['AAPL', 'AAPL'],
#         'Order': ['BUY', 'SELL'],
#         'Shares': [10, 10]
#     }, index=pd.to_datetime(['2008-01-15', '2008-02-15']))
#
#     start_val = 100000  # Starting portfolio value
#     portvals = compute_portvals(trades_example, start_val)
#
#     print(portvals)

def compute_portvals(trades_df, start_val=100000, commission=0.00, impact=0.00):
    if trades_df.empty:
        print("DataFrame is empty!")
        return pd.DataFrame()

    symbols = trades_df['Symbol'].unique().tolist()
    start_date = trades_df.index.min()
    end_date = trades_df.index.max()

    price_data = get_data(symbols, pd.date_range(start_date, end_date), addSPY=True, colname='Adj Close')
    prices = price_data[symbols]
    prices['Cash'] = 1.0

    trades = pd.DataFrame(index=prices.index, columns=prices.columns)
    trades.fillna(0.0, inplace=True)
    trades['Cash'] = start_val

    for index, row in trades_df.iterrows():
        symbol = row['Symbol']
        shares = row['Shares']
        if shares > 0:
            order = 'BUY'
        else:
            order = 'SELL'
        price = prices.loc[index, symbol]
        trade_value = shares * price

        if order == 'BUY':
            trades.loc[index, symbol] += shares
            trades.loc[index, 'Cash'] -= trade_value * (1 + impact) + commission
        elif order == 'SELL':
            trades.loc[index, symbol] -= shares
            trades.loc[index, 'Cash'] += trade_value * (1 - impact) - commission

    holdings = trades.cumsum()
    value = holdings * prices
    portvals = value.sum(axis=1)

    return portvals.to_frame("Portfolio Value")

if __name__ == "__main__":
    test_code()

def author():
    return "jvarghese42"
#imports
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt

from util import *
from indicators import bollinger_bands, on_balance_volume, momentum, relative_strength_index

class ManualStrategy:
    def __init__(self, symbol="JPM", start_date=dt.datetime(2008, 1, 1), end_date=dt.datetime(2009, 12, 31), sv=100000):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.sv = sv

    def testPolicy(self):
        # Get price data using instance variables
        dates = pd.date_range(self.start_date, self.end_date)
        prices_all = get_data([self.symbol], dates)  # automatically adds SPY
        prices = prices_all[self.symbol]  # only portfolio symbols
        prices_SPY = prices_all['SPY']  # only SPY, for comparison later
        volumes_all = get_data([self.symbol], dates, addSPY=True, colname="Volume")  # Get volume data
        volumes = volumes_all['Volume'] if 'Volume' in prices_all.columns else pd.Series(index=prices.index, data=0)

        # Calculate indicators
        momentum_vals = momentum(prices)
        rm, upper_band, lower_band = bollinger_bands(self.start_date, self.end_date, self.symbol, window=20)
        rsi_vals = relative_strength_index(prices)
        # if 'Volume' in prices_all.columns:
        #     obv_vals = on_balance_volume(prices, volumes_all['Volume'])
        # else:
        #     print("Volume data is missing. Skipping OBV calculation.")
        #     obv_vals = pd.Series(index=prices.index, data=np.nan)  # Create a series of NaNs or zeros

        print(prices.shape)
        print(momentum_vals.shape)
        print(upper_band.shape)
        print(lower_band.shape)
        print(rsi_vals.shape)
        print(upper_band.columns)
        print(lower_band.columns)

        # Combine indicators into a DataFrame
        indicators = pd.DataFrame({
            'Price': prices,
            'Momentum': momentum_vals,
            'Upper Band': upper_band[self.symbol],
            'Lower Band': lower_band[self.symbol],
            'RSI': rsi_vals
            #'OBV': obv_vals #add comma to preceding line
        })


        # Generate signals
        indicators['Signal'] = 0
        indicators.loc[indicators['Price'] < indicators['Lower Band'], 'Signal'] = 1
        indicators.loc[indicators['Price'] > indicators['Upper Band'], 'Signal'] = -1

        # Apply trading logic
        trades = indicators['Signal'].copy()
        trades[(indicators['Momentum'] <= 0) | (indicators['RSI'] >= 70)] = 0
        trades[(indicators['Momentum'] >= 0) & (indicators['RSI'] <= 30)] = 1
        trades[(indicators['Momentum'] <= 0) & (indicators['RSI'] >= 70)] = -1

        # Calculate actual trades from signals
        trades = trades.diff().fillna(0)
        trades *= 1000  # Scaling trades to 1000 shares

        return trades, prices

    # Additional methods here

if __name__ == '__main__':
    ms = ManualStrategy()
    trades, prices = ms.testPolicy()
    print(trades.head())
    # Additional testing and plotting calls here

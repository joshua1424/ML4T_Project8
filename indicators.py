"""
"""
"""
Student Name: Joshua Varghese
GT User ID: jvarghese42	   		 	   			  		 			     			  	 
GT ID: 903508453 		
"""

"""
Code implementing your indicators as functions that operate on DataFrames.
The main method should generate charts that will illustrate your indicators in the report.
"""

# IMPORTS
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from util import get_data, plot_data
def momentum(prices):
    df_temp = prices.copy()
    df_temp = (prices / prices.shift(10)) - 1 #Corrected indexing
    df_temp.iloc[0:10] = np.nan
    return df_temp


def bollinger_bands(sd, ed, symbol, window=20, num_std_dev=2, plot=False):
    dates = pd.date_range(sd, ed)
    prices = get_data([symbol], dates)
    prices = prices[[symbol]]
    prices = prices.ffill().bfill()

    # Calculate rolling mean and rolling standard deviation
    rm = prices.rolling(window=window, min_periods=window).mean()
    rstd = prices.rolling(window=window, min_periods=window).std()

    # Calculate upper and lower bands
    upper_band = rm + (rstd * num_std_dev)
    lower_band = rm - (rstd * num_std_dev)

    if plot:
        plt.figure(figsize=(14, 7))
        plt.plot(prices, label=f"{symbol} prices", color='blue')
        plt.plot(rm, label="Rolling Mean", color='orange')
        plt.fill_between(prices.index, lower_band.iloc[:, 0], upper_band.iloc[:, 0], color='gray', alpha=0.3,
                         label="Bollinger Bands")
        plt.title(f"Bollinger Bands for {symbol}")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plt.grid(True)
        #plt.show()

    return rm, upper_band, lower_band


def relative_strength_index(prices, window=14):
    delta = prices.diff(1)
    gain = (delta.where(delta > 0, 0)).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)

    avg_gain = gain.rolling(window=window, min_periods=window).mean()
    avg_loss = loss.rolling(window=window, min_periods=window).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

def on_balance_volume(prices, volume,  window=14):
    obv = volume.copy()
    obv.iloc[0] = 0 #starting value of obv

    for i in range(1, len(prices)):
        if prices.iloc[i] > prices.iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i-1]
        elif prices.iloc[i] < prices.iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
        else:
            obv.iloc[i] = obv.iloc[i-1]
    return obv


def author():
    return "jvarghese42"
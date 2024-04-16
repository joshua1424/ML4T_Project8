#imports
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt

from util import *
from indicators import bollinger_bands, on_balance_volume, momentum, relative_strength_index

class ManualStrategy:
    # Constructor and other methods...
    def __init__(self, symbol="JPM", start_date=dt.datetime(2008, 1, 1), end_date=dt.datetime(2009, 12, 31), sv = 100000):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date

    def testPolicy(self, symbol, sd, ed, sv=100000):
        print("1a")
        dates = pd.date_range(sd, ed)
        prices_all = get_data([symbol], dates)
        prices = prices_all[[symbol]].dropna()
        prices_SPY = prices_all["SPY"]  # For comparison

        # Ensure volume data is properly fetched and aligned
        volumes = get_data([symbol], dates, addSPY=True, colname="Volume")
        volumes = volumes['Volume'] if 'Volume' in volumes.columns else pd.Series(index=prices.index, data=0)

        print("1b")

        # Calculate indicators
        momentum_vals = momentum(prices)
        _, upper_band, lower_band = bollinger_bands(self.start_date, self.end_date, self.symbol)
        rsi_vals = relative_strength_index(prices)

        # Check if OBV can be calculated

        print("1c")
        # Combine indicators into a DataFrame
        indicators = pd.DataFrame({
            'Price': prices[symbol],  # Access the series directly
            'Momentum': momentum_vals,
            'Upper Band': upper_band[symbol],  # Access the series directly
            'Lower Band': lower_band[symbol],  # Access the series directly
            'RSI': rsi_vals
        }, index=prices.index)

        # Generate signals
        indicators['Signal'] = 0
        indicators.loc[indicators['Price'] < indicators['Lower Band'], 'Signal'] = 1  # Buy signal
        indicators.loc[indicators['Price'] > indicators['Upper Band'], 'Signal'] = -1  # Sell signal

        print("1d")

        # Apply trade logic
        trades = indicators['Signal'].diff().fillna(0)
        trades *= 1000  # Assuming each signal represents 1000 shares

        return trades, prices

    def plot_signals(self, trades):
        dates = pd.date_range(self.start_date, self.end_date)
        prices_all = get_data([self.symbol, 'SPY'], dates)
        prices = prices_all[[self.symbol]]

        fig, ax = plt.subplots(figsize=(12, 8))
        prices.plot(ax=ax, color='g', lw=1., legend=True)
        buy_trades = trades[trades > 0]
        sell_trades = trades[trades < 0]

        ax.plot(prices.loc[buy_trades.index], '^', markersize=10, color='k', lw=0, label='Buy Signal', marker='^')
        ax.plot(prices.loc[sell_trades.index], 'v', markersize=10, color='r', lw=0, label='Sell Signal', marker='v')

        ax.set_xlabel("Date")
        ax.set_ylabel("Price")
        ax.legend()
        plt.title(f"{self.symbol} Manual Strategy Trades")
        plt.grid(True)
        plt.show()

    def plot_benchmark(self, trades, symbol_prices, benchmark_prices, start_capital=100000):
        # Compute the cumulative returns for the benchmark
        benchmark_cum_ret = (benchmark_prices / benchmark_prices.iloc[0])

        # Compute the portfolio values from trades
        holdings = trades.cumsum() + start_capital / symbol_prices.iloc[0]  # Normalize initial holdings to match benchmark
        port_val = holdings * symbol_prices

        # Compute the cumulative returns for your strategy
        strategy_cum_ret = (port_val / port_val.iloc[0])

        # Plot the benchmark and strategy cumulative returns
        plt.figure(figsize=(14, 7))
        benchmark_cum_ret.plot(label="Benchmark", color='blue')
        strategy_cum_ret.plot(label="Strategy", color='green')
        plt.title("Benchmark vs Strategy Cumulative Returns")
        plt.legend(loc='best')
        plt.xlabel("Date")
        plt.ylabel("Cumulative Returns")
        plt.grid(True)
        plt.show()

    def calculate_sharpe_ratio(self, trades, symbol_prices):
        initial_cap = 100000
        portfolio_values = initial_cap + (trades * symbol_prices).cumsum()
        daily_returns = portfolio_values.pct_change().dropna()
        sharpe_ratio = daily_returns.mean() / daily_returns.std() * np.sqrt(252)  # Annualized Sharpe Ratio
        return sharpe_ratio


    def author():
      return 'jvarghese42' # replace tb34 with your Georgia Tech username.



if __name__ == '__main__':
    print("1")
    ms = ManualStrategy()
    print("2")
    trades, prices = ms.testPolicy(ms.symbol, ms.start_date, ms.end_date)
    print("3")
    ms.plot_signals(trades)

    # Get the benchmark prices for SPY
    spy_prices_all = get_data(['SPY'], pd.date_range(ms.start_date, ms.end_date))
    spy_prices = spy_prices_all['SPY']
    ms.plot_benchmark(trades, prices[ms.symbol], spy_prices)

    print("4")
    symbol_prices = prices[ms.symbol]
    sharpe_ratio = ms.calculate_sharpe_ratio(trades, symbol_prices)
    print(f"The Sharpe Ratio is: {sharpe_ratio}")

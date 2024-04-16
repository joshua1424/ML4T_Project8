#imports
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt

from util import *
from indicators import bollinger_bands, on_balance_volume, momentum, relative_strength_index
from marketsimcode import compute_portvals

class ManualStrategy:
    def __init__(self, symbol="JPM", start_date=dt.datetime(2010, 1, 1), end_date=dt.datetime(2011, 12, 31), sv = 100000):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.start_val = sv  # Starting value of the portfolio

    def testPolicy(self, sd, ed, symbol="JPM", sv=100000):
        #print("1a")
        dates = pd.date_range(self.start_date, self.end_date)
        prices_all = get_data([self.symbol], dates)
        prices = prices_all[[self.symbol]].dropna()
        prices_SPY = prices_all["SPY"] #For comparison

        #For OBV
        volumes_all = get_data([self.symbol], dates, addSPY=True, colname="Volume")  # Get volume data
        volumes = volumes_all['Volume'] if 'Volume' in prices_all.columns else pd.Series(index=prices.index, data=0)
        #print("1b")

        #calculate indicators
        momentum_vals = momentum(prices)
        _, upper_band, lower_band = bollinger_bands(self.start_date, self.end_date, self.symbol, num_std_dev=.68)
        rsi_vals = relative_strength_index(prices)

        # # Calculate OBV only if Volume data is available
        # if 'Volume' in prices_all.columns:
        #     obv_vals = on_balance_volume(prices, volumes_all['Volume'])
        # else:
        #     print("Volume data is missing. Skipping OBV calculation.")
        #     obv_vals = pd.Series(index=prices.index, data=np.nan)  # Create a series of NaNs or zeros


        #print("1c")

        # Combine indicators into a DataFrame
        indicators = pd.DataFrame({
            'Price': prices[self.symbol].squeeze(),
            'Momentum': momentum_vals.squeeze(),
            'Upper Band': upper_band[self.symbol].squeeze(),
            'Lower Band': lower_band[self.symbol].squeeze(),
            'RSI': rsi_vals.squeeze()
        }, index=prices.index)

        #Combine all indicators
        indicators['Signal'] = 0
        buy_signals = (indicators['Price'] < indicators['Lower Band']) & (indicators['Momentum'] > -.12) & (indicators['RSI'] < 34)
        sell_signals = (indicators['Price'] > indicators['Upper Band']) & (indicators['Momentum'] < .12) & (indicators['RSI'] > 66)

        #prices.join([momentum_vals, upper_band, lower_band, rsi_vals, obv_vals], how='inner')
        #print("1d")

        #Trading signals
        signals = pd.DataFrame(index=prices.index)
        signals['Signal'] = 0

        # buy_signals = (indicators['Price'] < indicators['Lower Band']) & (indicators['RSI'] < 50)
        # sell_signals = (indicators['Price'] > indicators['Upper Band']) & (indicators['RSI'] > 50)

        # Assume each trade is buying or selling 1000 shares
        trades = pd.Series(index=prices.index, data=0)
        trades[buy_signals] = 1000
        trades[sell_signals] = -1000
        trades = trades.diff().fillna(0)

        return trades, prices

    def add_evidence(self, symbol="JPM",
        # sd=dt.datetime(2008, 1, 1),
        # ed=dt.datetime(2009, 1, 1),
        # sv=10000):
        pass

    def plot_performance(self, symbol_prices, trades, benchmark_prices, title='Manual Strategy Performance',
                         filename='ManualStrategyIn.png'):
        start_val = 100000
        stock_positions = trades.cumsum()
        stock_values = stock_positions * symbol_prices
        portfolio_values = start_val + stock_values.cumsum()
        normalized_portfolio = portfolio_values / portfolio_values.iloc[0]
        normalized_benchmark = benchmark_prices / benchmark_prices.iloc[0]

        # Plotting
        plt.figure(figsize=(14, 7))
        normalized_benchmark.plot(color='purple', label='Benchmark (Hold 1000 Shares of JPM)')
        normalized_portfolio.plot(color='red', label='Manual Strategy')

        # Adding vertical lines for trade signals
        for date in trades[trades > 0].index:
            plt.axvline(x=date, color='blue', linestyle='--', lw=0.5,
                        label='Buy Signal' if date == trades[trades > 0].index[0] else "")
        for date in trades[trades < 0].index:
            plt.axvline(x=date, color='black', linestyle='--', lw=0.5,
                        label='Sell Signal' if date == trades[trades < 0].index[0] else "")

        plt.title(title)
        plt.xlabel('Date')
        plt.ylabel('Normalized Value')
        plt.legend()
        plt.grid(True)
        plt.savefig(filename)
        #plt.show()

    def author():
      return 'jvarghese42' # replace tb34 with your Georgia Tech username.

    def calculate_sharpe_ratio(self, trades, symbol_prices):
        initial_cap = 100000
        portfolio_values = initial_cap + (trades * symbol_prices).cumsum()
        daily_returns = portfolio_values.pct_change().dropna()
        std_dev = daily_returns.std()
        if std_dev != 0:
            sharpe_ratio = (daily_returns.mean() / std_dev) * np.sqrt(252)  # Annualized Sharpe Ratio
        else:
            sharpe_ratio = np.nan  # or set it to some default value or raise an error
        return sharpe_ratio

def calculate_cumulative_return(portfolio_values):
    """Calculate the cumulative return of the portfolio over the trading period."""
    cumulative_return = (portfolio_values.iloc[-1] / portfolio_values.iloc[0]) - 1
    return cumulative_return


if __name__ == '__main__':
#print("1")
    ms = ManualStrategy()
#print("2")
    trades, prices = ms.testPolicy(sd=ms.start_date, ed=ms.end_date, sv=100000)
#print("3")
    spy_prices_all = get_data(['SPY'], pd.date_range(ms.start_date, ms.end_date))
    spy_prices = spy_prices_all['SPY']
    symbol_prices = prices[ms.symbol]

    ms.plot_performance(prices[ms.symbol], trades, spy_prices)
    ms.plot_performance(prices[ms.symbol], trades, spy_prices, filename=ManualStrategyOut)

#print("4")
    strategy_portfolio_values = 100000 + (trades * prices[ms.symbol]).cumsum()
    benchmark_portfolio_values = 100000 * (spy_prices / spy_prices.iloc[0])

    # Calculate cumulative returns for both portfolios
    strategy_cumulative_return = calculate_cumulative_return(strategy_portfolio_values)
    benchmark_cumulative_return = calculate_cumulative_return(benchmark_portfolio_values)

    # Calculate daily returns for both portfolios
    strategy_daily_returns = strategy_portfolio_values.pct_change().dropna()
    benchmark_daily_returns = benchmark_portfolio_values.pct_change().dropna()

    # Calculate standard deviation of daily returns
    strategy_std_daily_returns = strategy_daily_returns.std()
    benchmark_std_daily_returns = benchmark_daily_returns.std()

    # Calculate average daily returns
    strategy_avg_daily_returns = strategy_daily_returns.mean()
    benchmark_avg_daily_returns = benchmark_daily_returns.mean()

    # Print results
    print(f"Strategy Cumulative Return: {strategy_cumulative_return}")
    print(f"Benchmark Cumulative Return: {benchmark_cumulative_return}")
    print(f"Strategy Std of Daily Returns: {strategy_std_daily_returns}")
    print(f"Benchmark Std of Daily Returns: {benchmark_std_daily_returns}")
    print(f"Strategy Average Daily Returns: {strategy_avg_daily_returns}")
    print(f"Benchmark Average Daily Returns: {benchmark_avg_daily_returns}")


    sharpe_ratio = ms.calculate_sharpe_ratio(trades, prices[ms.symbol])
    print(f"The Sharpe Ratio is: {sharpe_ratio}")

    # # Calculate cumulative returns
    # trades, prices = ms.testPolicy(sd=ms.start_date, ed=ms.end_date, sv=100000)
    # strategy_portvals = compute_portvals(
    #     trades_df=trades,
    #     start_val=100000,
    #     commission=9.95,
    #     impact=0.005
    # )
    #
    # benchmark_trades = pd.DataFrame(data=np.zeros(len(prices.index)), index=prices.index, columns=['Trades'])
    # benchmark_trades.iloc[0] = 1000  # Buy 1000 shares on the first day
    # benchmark_portvals = compute_portvals(
    #     trades_df=benchmark_trades,
    #     start_val=100000,
    #     commission=9.95,
    #     impact=0.005
    # )

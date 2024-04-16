import random
import datetime as dt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from marketsimcode import compute_portvals
from util import get_data
import ManualStrategy as ms
import StrategyLearner as sl
from marketsimcode import compute_portvals
from experiment1 import run_experiment1
from experiment2 import run_experiment2


def calculate_sharpe_ratio(portfolio_values):
    daily_returns = portfolio_values.pct_change().dropna()
    std_dev = daily_returns.std()
    if std_dev != 0:
        return (daily_returns.mean() / std_dev) * np.sqrt(252)
    return np.nan

def calculate_cumulative_return(portfolio_values):
    return (portfolio_values.iloc[-1] / portfolio_values.iloc[0]) - 1

def author():
    return "jvarghese42"

def run_strategy():
    start_date = dt.datetime(2008, 1, 1)
    end_date = dt.datetime(2009, 12, 31)
    starting_value = 100000
    symbol = "JPM"

    strategy = ms.ManualStrategy()
    trades = strategy.testPolicy(symbol=symbol, sd=start_date, ed=end_date, sv=starting_value)
    prices = get_data([symbol], pd.date_range(start_date, end_date), addSPY=False)

    portvals = compute_portvals(trades, start_val=starting_value, commission=9.95, impact=0.005)
    normalized_portvals = portvals / portvals.iloc[0]

    benchmark_trades = pd.DataFrame(data=np.zeros(len(prices.index)), index=prices.index, columns=[symbol])
    benchmark_trades.iloc[0, 0] = 1000
    benchmark_vals = compute_portvals(benchmark_trades, start_val=starting_value, commission=9.95, impact=0.005)
    normalized_benchmark = benchmark_vals / benchmark_vals.iloc[0]

    sharpe_ratio = calculate_sharpe_ratio(normalized_portvals)
    cumulative_return = calculate_cumulative_return(normalized_portvals)

    plt.figure(figsize=(10, 5))
    plt.plot(normalized_portvals, label='Strategy Portfolio')
    plt.plot(normalized_benchmark, label='Benchmark Portfolio')
    plt.title('Comparison of Manual Strategy and Benchmark')
    plt.xlabel('Date')
    plt.ylabel('Normalized Portfolio Value')
    plt.legend()
    plt.show()

    print(f"Sharpe Ratio: {sharpe_ratio}")
    print(f"Cumulative Return: {cumulative_return}")

if __name__ == "__main__":
    run_strategy()

import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import numpy as np

from StrategyLearner import StrategyLearner
from marketsimcode import compute_portvals
from util import get_data


def run_experiment2():

    # In-sample
    start_date = dt.datetime(2008, 1, 1)
    end_date = dt.datetime(2009, 12, 31)
    starting_value = 100000
    comm = 0
    ticker = "JPM"

    # initialize data structures
    avg_returns = []
    number_of_trades = []

    for impact in [0.0, 0.005, 0.01]:

        learner = StrategyLearner(impact=impact, verbose=False)
        learner.add_evidence(symbol=ticker, sd=start_date, ed=end_date, sv=starting_value)
        signals = learner.testPolicy(symbol=ticker, sd=start_date, ed=end_date, sv=starting_value)

        # Convert signals to trades
        trades = create_trade_orders(signals)

        # Create orders file
        orders_file = create_orders_file(trades, stock=ticker)

        # Get Portfolio Stats
        port_value = compute_portvals(orders_file, start_date, end_date, commission=comm, impact=impact)
        port_value = port_value / port_value.iloc[0]
        port_value = port_value.to_frame()

        # Update data
        avg_returns.append(np.mean(port_value.pct_change()))
        number_of_trades.append(len(orders_file))

    # Aggregate data and create charts
    avg = pd.DataFrame(data=np.array(avg_returns), index=[0.0, 0.005, 0.01])
    num_t = pd.DataFrame(data=np.array(number_of_trades), index=[0.0, 0.005, 0.01])

    # Comparative Charts
    # Chart 1: Average Returns vs Impact
    fig = plt.figure()
    plt.plot(avg, 'g')
    plt.legend(["Avg_return"])
    plt.xlabel("Impact")
    plt.ylabel("Metric Value")
    plt.title("Experiment 2, Avg_returns and Impact")
    plt.savefig("experiment2_avg_rets.png")
    plt.close()

    # Chart 2: Number of Trades vs Impact
    fig = plt.figure()
    plt.plot(num_t, 'r')
    plt.legend(["Number of Trades"])
    plt.xlabel("Impact")
    plt.ylabel("Metric Value")
    plt.title("Experiment 2, Number of Trades and Impact")
    plt.savefig("experiment2_num_trades.png")
    plt.close()


def create_trade_orders(signals):
    trades = pd.DataFrame(data=0, columns=["shares"], index=signals.index.values)

    for i in range(1, trades.shape[0]):
        if signals.iloc[i] != 0 and signals.iloc[i - 1] == 0:
            trades.iloc[i] = signals.iloc[i] * 1
        elif signals.iloc[i] == 0 and signals.iloc[i - 1] != 0:
            trades.iloc[i] = signals.iloc[i - 1] * -1
        elif signals.iloc[i] != signals.iloc[i - 1] and signals.iloc[i - 1] != 0:
            trades.iloc[i] = signals.iloc[i - 1] * -2
        elif signals.iloc[i] == signals.iloc[i - 1] and signals.iloc[i - 1] != 0:
            trades.iloc[i] = 0

    return trades * 1000


def create_orders_file(trades, stock="JPM"):
    orders = pd.DataFrame(index=trades.index.values, columns=["Symbol", "Order", "Shares"])
    orders["Symbol"] = stock
    orders["Order"] = trades.where(trades < 1, "BUY").where(trades >= 0, "SELL")
    orders["Shares"] = trades
    orders = orders.drop(orders[orders.Order == 0].index)
    return orders


if __name__ == "__main__":
    run_experiment2()


def author():
    return 'jvarghese42'

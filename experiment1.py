import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt

from ManualStrategy import ManualStrategy
from StrategyLearner import StrategyLearner
from marketsimcode import compute_portvals
from util import get_data


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


def create_orders_file(clean_trades, stock="JPM"):
    orders = pd.DataFrame(index=clean_trades.index.values, columns=["Symbol", "Order", "Shares"])
    orders["Symbol"] = stock
    orders["Order"] = clean_trades.where(clean_trades < 1, "BUY").where(clean_trades >= 0, "SELL")
    orders["Shares"] = clean_trades
    orders = orders.drop(orders[orders.Order == 0].index)
    return orders


def run_experiment1():
    start_date = dt.datetime(2008, 1, 1)
    end_date = dt.datetime(2009, 12, 31)
    starting_value = 100000
    impt = 0
    comm = 0
    ticker = "JPM"

    data = 1000 * get_data([ticker], pd.date_range(start_date, end_date), addSPY=True, colname="Adj Close").drop(columns="SPY")
    data["benchmark"] = data / data.iloc[0, 0]

    manual = ManualStrategy()
    trades = manual.testPolicy(symbol=ticker, sd=start_date, ed=end_date, sv=starting_value)
    orders_file = create_orders_file(clean_trades=trades, stock=ticker)
    ms_port_value = compute_portvals(orders_file, start_date, end_date, commission=comm, impact=impt) / starting_value

    learner = StrategyLearner()
    learner.add_evidence(symbol=ticker, sd=start_date, ed=end_date)
    trades = learner.testPolicy(symbol=ticker, sd=start_date, ed=end_date)
    orders_file = create_orders_file(clean_trades=trades, stock=ticker)
    sl_port_value = compute_portvals(orders_file, start_date, end_date, commission=comm, impact=impt) / starting_value

    fig = plt.figure()
    plt.plot(data.benchmark, 'g')
    plt.plot(ms_port_value, 'r')
    plt.plot(sl_port_value, 'b')
    plt.legend(["benchmark", "ManualStrategy", "StrategyLearner"])
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value")
    plt.title("Experiment1, Strategy Comparison")
    fig.autofmt_xdate()
    plt.savefig("experiment1.png")
    plt.close()

    pass

def author():
    return 'jvarghese42'
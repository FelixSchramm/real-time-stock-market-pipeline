"""Plot the year-to-date price of the Microsoft stock in euro.

Yahoo Finance quotes MSFT in USD. Each daily close is converted with the
EUR/USD rate of the same day.

Usage::

    python data_exploration/plot_prices.py
"""

import matplotlib.pyplot as plt
import yfinance as yf

COLOR = "#2a78d6"


def load_msft_eur():
    """Download the year-to-date daily MSFT close and convert it to euro.

    :return: Series with the MSFT closing price in EUR per trading day
    """
    close = yf.download(
        ["MSFT", "EURUSD=X"], period="ytd", interval="1d", progress=False
    )["Close"]
    # The FX series has its own trading calendar, so fill gaps before dividing.
    close["EURUSD=X"] = close["EURUSD=X"].ffill()
    return (close["MSFT"] / close["EURUSD=X"]).dropna()


def plot(price_eur, path):
    """Draw the price line with a marker on the last value and save it.

    :param price_eur: Series from :func:`load_msft_eur`
    :param path: output PNG path
    :return: None
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(price_eur.index, price_eur, color=COLOR, linewidth=2)
    ax.annotate(
        f"{price_eur.iloc[-1]:.2f} EUR",
        (price_eur.index[-1], price_eur.iloc[-1]),
        xytext=(6, 0),
        textcoords="offset points",
        va="center",
    )
    ax.set_title("Microsoft (MSFT) in Euro, Jahresbeginn bis heute")
    ax.set_xlabel("Datum")
    ax.set_ylabel("Schlusskurs in EUR")
    ax.grid(alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=150)


if __name__ == "__main__":
    series = load_msft_eur()
    plot(series, "data_exploration/prices.png")
    print(series.describe())

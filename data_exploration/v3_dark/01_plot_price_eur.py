"""Plot the year-to-date price of the Microsoft stock in euro (dark).

Same plot as ``v2_polished/01_plot_price_eur.py``. Each daily close is
converted with the EUR/USD rate of the same day.

Usage::

    python data_exploration/v3_dark/01_plot_price_eur.py
"""

import yfinance as yf
from ci import COLORS, end_label, german, month_axis, new_figure, save

# MSFT keeps slot 2 (blue) in every chart, AAPL slot 1.
COLOR = COLORS[1]


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
    """Draw the price line with a labeled dot on the last value and save it.

    :param price_eur: Series from :func:`load_msft_eur`
    :param path: output PNG path
    :return: None
    """
    fig, ax = new_figure(
        "Microsoft (MSFT) in Euro",
        f"Tagesschlusskurs in EUR, 1. Januar bis {price_eur.index[-1]:%d.%m.%Y}",
    )
    ax.plot(price_eur.index, price_eur, color=COLOR)
    end_label(
        ax,
        price_eur.index[-1],
        price_eur.iloc[-1],
        f"{german(price_eur.iloc[-1], 2)} €",
        COLOR,
    )
    month_axis(ax)
    save(fig, path)


if __name__ == "__main__":
    series = load_msft_eur()
    plot(series, "data_exploration/v3_dark/01_price_eur.png")
    print(series.describe())

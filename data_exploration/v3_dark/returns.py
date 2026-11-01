"""Shared return arithmetic for comparisons and the Microsoft benchmark."""


def drawdown(close):
    """Calculate drawdown from the running high in the supplied period.

    :param close: daily prices, Series or DataFrame
    :return: drawdown in percent, including zero on new highs
    """
    return close.div(close.cummax()).sub(1).mul(100)

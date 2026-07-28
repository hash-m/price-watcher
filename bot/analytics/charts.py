import io
import discord
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

from bot.analytics.stats import create_dataframe

def create_history_chart(product_name, snapshots):
    price_df = create_dataframe(snapshots)
    fig, axes = plt.subplots(figsize=(10, 5))

    record_dates = list(price_df["price"].index)
    record_prices = list(price_df["price"].values)

    today = datetime.date.today()

    if record_dates and record_dates[-1] != today:
        plot_dates = record_dates + [today]
        plot_prices = record_prices + [record_prices[-1]]
    else:
        plot_dates = record_dates
        plot_prices = record_prices

    x_positions = range(len(plot_dates))

    axes.plot(x_positions, plot_prices, marker='o', linestyle='-')
    axes.set_xticks(list(x_positions))
    axes.set_xticklabels(plot_dates, rotation=45, ha="right")
    axes.set_xlabel("Dates")
    axes.set_ylabel("Prices")
    axes.set_title(f"Price History - {product_name}")
    fig.autofmt_xdate()
    return fig


def convert_chart_to_png(fig, filename="chart.png"):
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=100)
    buffer.seek(0)
    plt.close(fig)
    return discord.File(buffer, filename=filename)
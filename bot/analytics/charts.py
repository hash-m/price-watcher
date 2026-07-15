import io
import discord
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from bot.analytics.stats import create_dataframe

def create_history_chart(product_name,snapshots):
    price_df = create_dataframe(snapshots)
    fig, axes = plt.subplots(figsize=(10, 5))

    axes.plot(price_df["price"].index, price_df["price"].values, label="Price", linewidth=1.5)

    axes.set_title(f"{product_name} — Price History")
    axes.set_xlabel("Date") 
    axes.set_ylabel("Price (£)")
    axes.grid(alpha=0.5)
    fig.autofmt_xdate()

    fig.tight_layout()
    return fig

def convert_chart_to_png(fig, filename="chart.png"):
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=100)
    buffer.seek(0)
    plt.close(fig)
    return discord.File(buffer, filename=filename)
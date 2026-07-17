import pandas as pd

def create_dataframe(snapshots):
    df = pd.DataFrame(snapshots,columns=['id','product_id','price','captured_at'])
    df = df.drop(columns=['id','product_id'])
    df["captured_at"] = pd.to_datetime(df["captured_at"])
    df = df.sort_values("captured_at")
    df = df.set_index("captured_at")
    return df

def get_alltime(df):
    high = df["price"].max()
    low  = df["price"].min()
    mean = df["price"].mean()
    return high, low, mean

def get_diff_from_init(df):
    first_price = df["price"].iloc[0]
    current_price = df["price"].iloc[-1]

    percentage_change = ((current_price - first_price) / first_price) * 100
    return percentage_change

def get_stats(snapshots):
    df = create_dataframe(snapshots)

    high, low, mean              = get_alltime(df)
    percentage                   = get_diff_from_init(df)

    return (high, low, mean, percentage)
import pandas as pd

def create_dataframe(snapshots):
    df = pd.DataFrame(snapshots,columns=['id','product_id','price','captured_at'])
    df = df.drop(columns=['id','product_id'])
    df["captured_at"] = pd.to_datetime(df["captured_at"])
    df = df.sort_values("captured_at")
    df = df.set_index("captured_at")
    return df

def get_smas(daily_df):
    sma_30d = daily_df.rolling(30).mean()
    sma_90d = daily_df.rolling(90).mean()
    return sma_30d,sma_90d

def get_volatility(daily_df):
    return daily_df.rolling(90).std()

def get_momentum(daily_df):
    window = daily_df.iloc[-90:]

    if len(window) < 2:
        return None

    current_price = window.iloc[-1]
    earliest_price = window.iloc[0]

    if earliest_price == 0:
        return None

    momentum = ((current_price - earliest_price) / earliest_price) * 100
    return momentum

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
    daily_prices = df["price"].resample("D").last().ffill()

    sma30d_series, sma90d_series = get_smas(daily_prices)
    volatility_series            = get_volatility(daily_prices)
    momentum                     = get_momentum(daily_prices)
    high, low, mean              = get_alltime(df)
    percentage                   = get_diff_from_init(df)

    sma30d     = sma30d_series.iloc[-1]     if len(sma30d_series)     else float("nan")
    sma90d     = sma90d_series.iloc[-1]     if len(sma90d_series)     else float("nan")
    volatility = volatility_series.iloc[-1] if len(volatility_series) else float("nan")

    return (sma30d, sma90d, volatility, momentum, high, low, mean, percentage)
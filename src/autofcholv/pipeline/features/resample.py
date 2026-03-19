import pandas as pd
import pandas_ta as ta


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    tmp_data = df.copy()
    tmp_data['day_high'] = tmp_data['High']
    tmp_data['day_low'] = tmp_data['Low']
    tmp_data['day_close'] = tmp_data['Close']
    tmp_data['day_open'] = tmp_data['Open']
    tmp_data['day_vol'] = tmp_data['Volume']
    daily_data = tmp_data.resample('D').agg({
            'day_high': 'max',
            'day_low': 'min',
            'day_close': 'last',
            'day_open': 'first',
            'day_vol': 'sum'
        })
    daily_data.dropna(subset=['day_high'], inplace=True)
    daily_data['day_pivot'] = (daily_data['day_high'] + daily_data['day_low'] + daily_data['day_close']) / 3
    daily_data['prev_day_close'] = daily_data['day_close'].shift(1)
    daily_data['prev_day_open'] = daily_data['day_open'].shift(1)
    daily_data['prev_day_high'] = daily_data['day_high'].shift(1)
    daily_data['prev_day_low'] = daily_data['day_low'].shift(1)
    daily_data['prev_day_vol'] = daily_data['day_vol'].shift(1)
    daily_data['prev_day_pivot'] = daily_data['day_pivot'].shift(1)
    #
    data = df.copy()
    data = data.assign(time_d=pd.PeriodIndex(data.index, freq='1D').to_timestamp())
    #
    merged_data = pd.merge(data, daily_data, left_on="time_d", right_index=True, how="left")
    merged_data = merged_data.drop(columns=['time_d'])
    return merged_data
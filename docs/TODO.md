# TODO: 


## Add

- [x] df['is_max_4'] = (df["High"] > df["High"].shift(1).rolling(3).max())
- [x] df['upper_wick_group'] = df.apply(lambda r: "Increase" if r["upper_shadow"] > r["prev_upper_shadow"] else "Not Increase", axis=1)
- [x] df['MFI_group'] = df.apply(lambda r: "Increase" if r["MFI_1d"] > r["prev_MFI_1d"] else "Not Increase", axis=1)
- [x] df['higher_high_lower_vol'] = df.apply(lambda r: True if (r["High"] > r["prev_High"] and r["Volume"] < r["prev_Vol"]) else False, axis=1) 
- [x] df['Volume_higher_avg'] = df.apply(lambda r: True if r["Volume"] > r["avg_Volume"] else False, axis=1)
- [x] df['Volume_vs_prev_Vol'] = df.apply(lambda r: "Increase" if r["Volume"] > r["prev_Vol"] else "Not Increase", axis=1)
- [x] df['Volume_avg_group'] = df.apply(lambda r: "Increase" if r["Volume_avg"] > r["prev_Volume_avg"] else "Not Increase", axis=1)
- [x] def get_close_price_position(r):
    if r["Close"] > r["prev_High"]:
        return "> prev High"
    if r["Close"] > max(r["prev_Close"], r["prev_Open"]):
        return "Bong nen tren "
    if max(r["prev_Close"], r["prev_Open"]) > r["Close"] > min(r["prev_Close"], r["prev_Open"]):
        return "Than nen"
    if r["Close"] < min(r["prev_Close"], r["prev_Open"]):
        return "Bong nen duoi"
    if r["Close"] < r["prev_Low"]:
        return "< prev Low" 

    df['close_price_group'] = df.apply(lambda r: get_close_price_position(r), axis=1)

- [x] 
  def get_open_price_position(r):
      if r["Open"] > r["prev_Close"]:
          return "Open > prev_Close"
      if r["Open"] == r["prev_Close"]:
          return "Open = prev_Close"
      if r["Open"] < r["prev_Close"]:
          return "Open < prev_Close"

  df['opene_price_group'] = df.apply(lambda r: get_open_price_position(r), axis=1)

- [x] df['High_position'] = df.apply(lambda r: '> upper BB' if r["High"] > r["UB"] else '< upper BB', axis=1)

- [x] df["BB_rejection"] = df.apply(lambda r: True if r["Close"] < r["UB"] else False, axis=1)
- [x] df['lower_shadow_group'] = df.apply(lambda r: "Increase" if r["lower_shadow"] > r["prev_lower_shadow"] else "Increase", axis=1)
- [x]
    def get_ibs_vol_group(r):
      if r["Volume"] > r["prev_Vol"] and r["ibs"] > r["prev_ibs"]:
          return "Vol up, ibs incre"
      if r["Volume"] > r["prev_Vol"] and r["ibs"] < r["prev_ibs"]:
          return "Vol up, ibs decr"
      if r["Volume"] < r["prev_Vol"] and r["ibs"] > r["prev_ibs"]:
          return "Vol down, ibs incre"
      if r["Volume"] < r["prev_Vol"] and r["ibs"] < r["prev_ibs"]:
          return "Vol down, ibs decr"

      df["ibs_vol_group"] = df.apply(lambda r: get_ibs_vol_group(r) , axis=1)

- [x] df['rsi_area'] = df.apply(lambda r: '>55' if r["RSI20"] > 55 else ('<45' if r["RSI20"] < 45 else '45-55'), axis=1)
- [x] df['lower_low_lower_vol'] = df.apply(lambda r: True if (r["Low"] < r["prev_Low"] and r["Volume"] < r["prev_Vol"]) else False, axis=1)
- [x] df['Low_position'] = df.apply(lambda r: '> lower BB' if r["Low"] > r["LB"] else '<= lower BB', axis=1)
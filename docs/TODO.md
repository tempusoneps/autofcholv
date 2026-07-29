# TODO: 


## Add

- [ ] df['is_max_4'] = (df["High"] > df["High"].shift(1).rolling(3).max())
- [ ] ana_data['upper_wick_group'] = ana_data.apply(lambda r: "Increase" if r["upper_shadow"] > r["prev_upper_shadow"] else "Not Increase", axis=1)
- [ ] ana_data['MFI_group'] = ana_data.apply(lambda r: "Increase" if r["MFI_1d"] > r["prev_MFI_1d"] else "Not Increase", axis=1)
- [ ] ana_data['higher_high_lower_vol'] = ana_data.apply(lambda r: True if (r["High"] > r["prev_High"] and r["Volume"] < r["prev_Vol"]) else False, axis=1) 
- [ ] ana_data['Volume_higher_avg'] = ana_data.apply(lambda r: True if r["Volume"] > r["avg_Volume"] else False, axis=1)
- [ ] ana_data['Volume_vs_prev_Vol'] = ana_data.apply(lambda r: "Increase" if r["Volume"] > r["prev_Vol"] else "Not Increase", axis=1)
- [ ] ana_data['Volume_avg_group'] = ana_data.apply(lambda r: "Increase" if r["Volume_avg"] > r["prev_Volume_avg"] else "Not Increase", axis=1)
- [ ] def get_close_price_position(r):
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

    ana_data['close_price_group'] = ana_data.apply(lambda r: get_close_price_position(r), axis=1)

- [ ] 
  def get_open_price_position(r):
      if r["Open"] > r["prev_Close"]:
          return "Open > prev_Close"
      if r["Open"] == r["prev_Close"]:
          return "Open = prev_Close"
      if r["Open"] < r["prev_Close"]:
          return "Open < prev_Close"

  ana_data['opene_price_group'] = ana_data.apply(lambda r: get_open_price_position(r), axis=1)

- [ ] ana_data['High_position'] = ana_data.apply(lambda r: '> upper BB' if r["High"] > r["UB"] else '< upper BB', axis=1)

- [ ] ana_data["BB_rejection"] = ana_data.apply(lambda r: True if r["Close"] < r["UB"] else False, axis=1)
- [ ] ana_data['lower_shadow_group'] = ana_data.apply(lambda r: "Increase" if r["lower_shadow"] > r["prev_lower_shadow"] else "Increase", axis=1)
- [ ]
    def get_ibs_vol_group(r):
      if r["Volume"] > r["prev_Vol"] and r["ibs"] > r["prev_ibs"]:
          return "Vol up, ibs incre"
      if r["Volume"] > r["prev_Vol"] and r["ibs"] < r["prev_ibs"]:
          return "Vol up, ibs decr"
      if r["Volume"] < r["prev_Vol"] and r["ibs"] > r["prev_ibs"]:
          return "Vol down, ibs incre"
      if r["Volume"] < r["prev_Vol"] and r["ibs"] < r["prev_ibs"]:
          return "Vol down, ibs decr"

      ana_data["ibs_vol_group"] = ana_data.apply(lambda r: get_ibs_vol_group(r) , axis=1)

- ana_data['rsi_area'] = ana_data.apply(lambda r: '>55' if r["RSI20"] > 55 else ('<45' if r["RSI20"] < 45 else '45-55'), axis=1)
- ana_data['lower_low_lower_vol'] = ana_data.apply(lambda r: True if (r["Low"] < r["prev_Low"] and r["Volume"] < r["prev_Vol"]) else False, axis=1)
- ana_data['Low_position'] = ana_data.apply(lambda r: '> lower BB' if r["Low"] > r["LB"] else '<= lower BB', axis=1)
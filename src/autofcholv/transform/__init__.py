from pathlib import Path

VN30F1M_DIR = Path(__file__).parent.parent
OHLCV_DIR = VN30F1M_DIR / "data_ohlcv"
DATA_READY_DIR = VN30F1M_DIR / "data_ready"

COLUMN_SCHEMA = {

    # =========================
    # ORIGINAL OHLCV
    # =========================
    "Open": {"type": "float", "comment": "Giá mở cửa"},
    "High": {"type": "float", "comment": "Giá cao nhất"},
    "Low": {"type": "float", "comment": "Giá thấp nhất"},
    "Close": {"type": "float", "comment": "Giá đóng cửa"},
    "Volume": {"type": "float", "comment": "Khối lượng giao dịch"},

    # =========================
    # DAY DATA RESAMPLE
    # =========================
    "day_open": {"type": "float", "comment": "Giá mở cửa trong ngày"},
    "day_high": {"type": "float", "comment": "Giá cao nhất trong ngày"},
    "day_low": {"type": "float", "comment": "Giá thấp nhất trong ngày"},
    "day_close": {"type": "float", "comment": "Giá đóng cửa trong ngày"},
    "day_volume": {"type": "float", "comment": "Khối lượng giao dịch trong ngày"},

    # =========================
    # TIME FEATURES
    # =========================
    "hour": {"type": "int", "comment": "Giờ giao dịch"},
    "minute": {"type": "int", "comment": "Phút giao dịch"},
    "session_progress": {"type": "float", "comment": "Vị trí trong phiên"},
    "week_day": {"type": "int", "comment": "Ngày trong tuần"},

    # =========================
    # CANDLESTICK FEATURES
    # =========================
    "body": {"type": "float", "comment": "Thân nến abs(Close - Open)"},
    "upper_wick": {"type": "float", "comment": "Bóng nến trên"},
    "lower_wick": {"type": "float", "comment": "Bóng nến dưới"},
    "upper_wick_ratio": {"type": "float", "comment": "Tỷ lệ bóng nến trên"},
    "lower_wick_ratio": {"type": "float", "comment": "Tỷ lệ bóng nến dưới"},
    "candlestick_height": {"type": "float", "comment": "Chiều cao nến"},
    "ibs": {"type": "float", "comment": "Internal Bar Strength"},
    "clv": {"type": "float", "comment": "Close Location Value ((Close-Low) - (High-Close)) / (High - Low)"},
    "cbr": {"type": "float", "comment": "Candlestick Body Ratio (|Close - Open| / (High - Low))"},
    "candle_color": {"type": "string", "comment": "Màu nến (green/red/doji)"},

    # =========================
    # VOLUME FEATURES
    # =========================
    "volume_avg20": {"type": "float", "comment": "Trung bình khối lượng 20 phiên"},
    "volume_zscore": {"type": "float", "comment": "Z-score khối lượng"},
    "is_volume_above_avg": {"type": "bool", "comment": "Volume cao hơn trung bình"},

    # =========================
    # PRICE STRUCTURE
    # =========================
    "is_fvg": {"type": "bool", "comment": "Fair Value Gap"},
    "is_lower_low_higher_volume": {"type": "bool", "comment": "Đáy thấp hơn với volume cao hơn"},
    "high_position": {"type": "string", "comment": "Vị trí High so với Bollinger Band"},
    "low_position": {"type": "string", "comment": "Vị trí Low"},


    # =========================
    # TECHNICAL INDICATORS
    # =========================
    "EMA20": {"type": "float", "comment": "Exponential Moving Average 20"},
    "EMA250": {"type": "float", "comment": "Exponential Moving Average 250"},
    "ATR14": {"type": "float", "comment": "Average True Range 14"},
    "ADX14": {"type": "float", "comment": "Average Directional Index 14"},
    "RSI20": {"type": "float", "comment": "Relative Strength Index 20"},
    "RSI10": {"type": "float", "comment": "Relative Strength Index 10"},
    "VWAP": {"type": "float", "comment": "Volume Weighted Average Price"},
    "RSI_slope": {"type": "float", "comment": "Slope của RSI"},
    "EMA20_slope": {"type": "float", "comment": "Slope của EMA20"},
    "z_score": {"type": "float", "comment": "Z-score của Close = (Price-MA)/Std"},
    "pct_change": {"type": "float", "comment": "Phần trăm thay đổi"},
    "skew_100": {"type": "float", "comment": "df['pct_change'].rolling(100).skew()"},
    "kurt_100": {"type": "float", "comment": "df['pct_change'].rolling(100).kurt()"},
    "typical_price": {"type": "float", "comment": "(High+Low+Close)/3"},
    "money_flow": {"type": "float", "comment": "Money Flow = Typical Price * Volume"},
    "money_flow_type": {"type": "float", "comment": "Positive Flow if typical_price > prev_typical_price else Negative Flow"},
    "money_flow_score": {"type": "float", "comment": "Money Flow Score = sum(Positive Flow) / sum(Negative Flow)"},
    "DM": {"type": "float", "comment": "Distance Moved (DM) = (Current High + Current Low) / 2 - (Previous High + Previous Low) / 2"},
    "VBR": {"type": "float", "comment": "Volume Box Ratio = Volume / (High - Low)"},
    "EOM": {"type": "float", "comment": "Ease of Movement = DM / VBR"},
    "keltner_channel": {"type": "float", "comment": "Keltner Channel = EMA20 ± ATR14"},
    "hurst_exponent": {"type": "float", "comment": "Hurst Exponent 10"},
    "hurst_exponent_100": {"type": "float", "comment": "Hurst Exponent 100"},
    "parkinson_vol_20": {"type": "float", "comment": "Rolling 20 Parkinson Volatility"},
    "up_streak": {"type": "int", "comment": "Số phiên tăng liên tiếp"},
    "down_streak": {"type": "int", "comment": "Số phiên giảm liên tiếp"},
    # ====
    # CUSTOM MONEY FLOW
    # ====
    "MFM": {"type": "float", "comment": "Money Flow Multiplier (MFM)"},
    "MFV": {"type": "float", "comment": "Money Flow Volume (MFV)"},
    "CMF": {"type": "float", "comment": "Chaikin Money Flow (CMF) - volume-weighted momentum"},
    "CMF_3D": {"type": "float", "comment": "Chaikin Money Flow 3 ngày(3 * 49 bars)"},
    "CMF_5D": {"type": "float", "comment": "Chaikin Money Flow 5 ngày(5 * 49 bars)"},
    "CMF_10D": {"type": "float", "comment": "Chaikin Money Flow 10 ngày(10 * 49 bars)"},
    "MFI_1D": {"type": "float", "comment": "Money Flow Index 1 ngày"},
    "MFI_3D": {"type": "float", "comment": "Money Flow Index 3 ngày(3 * 49 bars)"},
    "MFI_5D": {"type": "float", "comment": "Money Flow Index 5 ngày(5 * 49 bars)"},
    "MFI_10D": {"type": "float", "comment": "Money Flow Index 10 ngày(10 * 49 bars)"},

    # ====
    # BOLLINGER BANDS
    # ====
    "BB_middle": {"type": "float", "comment": "Middle Band (SMA20)"},
    "BB_std": {"type": "float", "comment": "Độ lệch chuẩn 20 phiên"},
    "BB_upper": {"type": "float", "comment": "Upper Bollinger Band"},
    "is_bb_rejection": {"type": "bool", "comment": "Tín hiệu từ chối Bollinger Bands"},

    # =========================
    # PREVIOUS (SHIFTED) DATA
    # =========================
    "prev_Open": {"type": "float", "comment": "Open phiên trước"},
    "prev_High": {"type": "float", "comment": "High phiên trước"},
    "prev_Low": {"type": "float", "comment": "Low phiên trước"},
    "prev_Close": {"type": "float", "comment": "Close phiên trước"},
    "prev_Volume": {"type": "float", "comment": "Volume phiên trước"},
    "prev_body": {"type": "float", "comment": "Body phiên trước"},
    "prev_upper_wick": {"type": "float", "comment": "Upper wick phiên trước"},
    "prev_lower_wick": {"type": "float", "comment": "Lower wick phiên trước"},
    "prev_EMA20": {"type": "float", "comment": "EMA20 phiên trước"},
    "prev_EMA250": {"type": "float", "comment": "EMA250 phiên trước"},
    "prev_MFI_1D": {"type": "float", "comment": "MFI phiên trước"},
    "prev_ibs": {"type": "float", "comment": "IBS phiên trước"},

    # =========================
    # CUSTOM INDICATORS
    # =========================
    "fea_g1_001": {"type": "float", "comment": "100 * (Close - day_close.shift(1)) / day_close.shift(1)"},
    "fea_g1_002": {"type": "float", "comment": "(Close - close.shift(49)) / (max_high_49bars - min_low_49bars)"},

    # =========================
    # GROUPED FEATURES
    # =========================
    "high_volume_group": {"type": "string", "comment": "Nhóm High và Volume"},
    "volume_group": {"type": "string", "comment": "Nhóm Volume"},
    "price_body_group": {"type": "string", "comment": "Nhóm giá so với body"},
    "upper_wick_group": {"type": "string", "comment": "Nhóm upper wick"},
    "lower_wick_group": {"type": "string", "comment": "Nhóm lower wick"},
    "ibs_volume_group": {"type": "string", "comment": "Nhóm IBS và Volume"},
    "volume_avg_group": {"type": "string", "comment": "Nhóm volume trung bình"},
    "high_rsi_group": {"type": "bool", "comment": "Nhóm High và RSI"},
    "close_position_group": {"type": "string", "comment": "Nhóm vị trí Close"},
    "open_position_group": {"type": "string", "comment": "Nhóm vị trí Open"},

    # =========================
    # SIGNALS
    # =========================
    "couple_candle_cond_1": {"type": "string", "comment": "Điều kiện 1 cặp nến"},
    "couple_candle_cond_2": {"type": "string", "comment": "Điều kiện 2 cặp nến"},
    "couple_candle_signal": {"type": "string", "comment": "Tín hiệu cặp nến"},
    "ema_cross_signal": {"type": "string", "comment": "Tín hiệu giao cắt EMA20/EMA250"},
}
from autofcholv.pipeline.features.close import extract_features as extract_close_features
from autofcholv.pipeline.features.mix import extract_features as extract_mix_features


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    df = extract_close_features(df)
    df = extract_mix_features(df)
    return df
from collections.abc import Sequence

import pandas as pd


def as_feature_frame(values: Sequence[float], feature_columns: Sequence[str]) -> pd.DataFrame:
    if len(values) != len(feature_columns):
        raise ValueError(f"Expected {len(feature_columns)} features, received {len(values)}")
    return pd.DataFrame([list(values)], columns=list(feature_columns))

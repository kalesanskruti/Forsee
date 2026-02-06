from typing import List, Dict
import numpy as np

class FeatureEngineer:
    def __init__(self, window_size: int = 30):
        self.window_size = window_size
        
    def process_timeseries(self, df, feature_cols: List[str]):
        """
        Applies rolling mean, std, trend, rate of change
        """
        # Example pandas operations
        result = df.copy()
        for col in feature_cols:
            result[f"{col}_mean"] = df[col].rolling(window=self.window_size).mean()
            result[f"{col}_std"] = df[col].rolling(window=self.window_size).std()
            # result[f"{col}_trend"] = ... # polyfit slope
        
        return result.dropna()

feature_engineer = FeatureEngineer()

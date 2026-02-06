from typing import Dict, Any, List, Optional, Type
import logging

class ModelSelectionEngine:
    """
    Selects the best model architecture based on:
    - Task (RUL, Precursor, Clustering, Drift)
    - Problem Type (Regression, Classification, etc.)
    - Asset Type
    - Dataset Properties (Temporal, Size, Noise)
    """

    TASKS = {
        "RUL": "Regression",
        "PRECURSOR": "Classification",
        "CLUSTERING": "Clustering",
        "DRIFT": "Distribution Monitoring"
    }

    # Algorithm registry mapping
    ALGORITHMS = {
        "LSTM": "LSTMRegressor",
        "GRADIENT_BOOSTING_REG": "GradientBoostingRegressor",
        "RANDOM_FOREST_CLF": "RandomForestClassifier",
        "XGBOOST_CLF": "XGBoostClassifier",
        "KMEANS": "KMeansClustering",
        "DBSCAN": "DBSCANClustering",
        "ISOLATION_FOREST": "IsolationForestAnomaly"
    }

    @staticmethod
    def select_model(task_type: str, dataset_props: Dict[str, Any]) -> str:
        """
        Returns the algorithm key.
        """
        task = task_type.upper()
        
        if task == "RUL":
            if dataset_props.get("temporal", False):
                return "LSTM"
            else:
                return "GRADIENT_BOOSTING_REG"
        
        elif task == "PRECURSOR":
            # For classification
            sample_count = dataset_props.get("sample_count", 0)
            if sample_count > 50000: # Threshold for XGBoost preference
                return "XGBoost" # Mapped to XGBOOST_CLF later or handled flexibly
            return "RANDOM_FOREST_CLF"
            
        elif task == "CLUSTERING":
            return "KMEANS" # Default, could check noise for DBSCAN
            
        return "RANDOM_FOREST_CLF" # Fallback

model_selector = ModelSelectionEngine()

from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import pandas as pd
import numpy as np

class DataQualityService:
    @staticmethod
    def validate_input(data: Dict[str, Any], schema_rules: Optional[Dict] = None) -> List[str]:
        """
        Validate input dictionary against quality rules.
        Returns a list of error messages. if empty, data is valid.
        """
        errors = []
        
        # 1. Check Missing Values (NaN, None)
        # Convert to DF for easier checking if complex structure, or dict iteration
        for key, value in data.items():
            if value is None:
                errors.append(f"Missing value for feature: {key}")
            elif isinstance(value, (int, float)) and np.isnan(value):
                 errors.append(f"NaN value for feature: {key}")
        
        # 2. Check Range (Basic Sanity)
        # In a real system, these rules would come from a database or config registry
        # Hardcoded Example for predictive maintenance sensors
        
        # Sensor 11 creates frequent issues in CMAPSS data
        if "s11" in data:
            if not (0 <= data["s11"] <= 1000): # Hypothetical range
                errors.append(f"Value for s11 out of physical range: {data['s11']}")

        # 3. Stuck Sensor Check
        # Would require history, simplified here to check if variance is 0 if time-series list provided
        # processing skipped for single-point prediction context
        
        return errors

data_quality_service = DataQualityService()

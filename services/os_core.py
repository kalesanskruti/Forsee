from typing import Dict, Any, List
import uuid

class SimulationService:
    def run_simulation(self, model_id: uuid.UUID, scenario_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs 'What-If' scenarios.
        Example Config: { "load_increase": 0.2, "temp_offset": 5 }
        """
        # Logic: 
        # 1. Load active model
        # 2. Perturb input data according to scenario
        # 3. Run inference
        # 4. Compare with baseline
        
        return {
            "scenario": scenario_config,
            "projected_rul": 150,
            "baseline_rul": 200,
            "risk_impact": "HIGH",
            "simulation_id": str(uuid.uuid4())
        }

class RecommendationEngine:
    def generate_recommendations(self, prediction_result: Dict[str, Any], asset_type: str) -> List[str]:
        """
        Maps technical prediction (RUL=5, Risk=0.9) to human actions.
        """
        actions = []
        risk = prediction_result.get("risk_score", 0)
        rul = prediction_result.get("rul", 999)
        
        if risk > 0.8:
            actions.append("Immediate Inspection Required")
        
        if rul < 10:
            actions.append(f"Schedule replacement for {asset_type} within 24 hours")
        elif rul < 50:
             actions.append("Order spare parts")
             
        return actions

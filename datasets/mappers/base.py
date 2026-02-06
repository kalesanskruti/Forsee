from typing import Dict, Any, List
import abc

class BaseDatasetMapper(abc.ABC):
    """
    Abstract Base Class for Dataset Mappers.
    Each mapper converts raw dataset files into canonical X (features) and y (labels).
    """
    
    @abc.abstractmethod
    def validate(self, path: str) -> bool:
        pass
        
    @abc.abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Returns inferred metadata like sampling_rate, temporal, etc."""
        pass
        
    @abc.abstractmethod
    def load_and_process(self, path: str, **kwargs) -> Dict[str, Any]:
        """
        Returns:
            {
                "X": np.array or pd.DataFrame,
                "y": np.array or pd.Series,
                "features": List[str],
                "metadata": Dict
            }
        """
        pass

class MapperFactory:
    _mappers = {}
    
    @classmethod
    def register(cls, key: str, mapper_cls):
        cls._mappers[key] = mapper_cls
        
    @classmethod
    def get_mapper(cls, key: str) -> BaseDatasetMapper:
        mapper = cls._mappers.get(key)
        if not mapper:
            raise ValueError(f"No mapper found for {key}")
        return mapper()

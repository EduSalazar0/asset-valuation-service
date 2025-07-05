from abc import ABC, abstractmethod
from typing import Optional
import uuid
from domain.entities.asset import Asset

class IAssetRepository(ABC):
    @abstractmethod
    def find_by_id(self, asset_id: uuid.UUID) -> Optional[Asset]:
        """Finds an asset by its unique ID."""
        pass
    
    @abstractmethod
    def save(self, asset: Asset) -> Asset:
        """Saves (updates) an asset entity."""
        pass
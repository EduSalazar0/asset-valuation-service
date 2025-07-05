from abc import ABC, abstractmethod
from domain.entities.asset import Asset

class IMessagingProducer(ABC):
    @abstractmethod
    def publish_asset_valuated(self, asset: Asset) -> None:
        """Publishes an event indicating an asset has been valuated."""
        pass
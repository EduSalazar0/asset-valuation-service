import uuid
from pydantic import BaseModel
from domain.enums.asset_type import AssetType

class AssetDiscoveredEvent(BaseModel):
    """Represents the data from the 'asset.discovered' event."""
    asset_id: uuid.UUID
    scan_id: uuid.UUID
    asset_type: AssetType
    value: str
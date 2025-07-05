import uuid
from typing import Optional
from pydantic import BaseModel, Field

from domain.enums.asset_type import AssetType

class Asset(BaseModel):
    id: uuid.UUID
    scan_id: uuid.UUID
    asset_type: AssetType
    value: str
    
    # New valuation fields
    sca: Optional[float] = None
    sca_c: Optional[float] = None
    sca_i: Optional[float] = None
    sca_d: Optional[float] = None

    class Config:
        from_attributes = True
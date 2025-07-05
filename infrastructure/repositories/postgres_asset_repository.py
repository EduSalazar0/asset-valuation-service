from typing import Optional
import uuid
from sqlalchemy.orm import Session
import logging

from domain.entities.asset import Asset
from domain.repositories.asset_repository import IAssetRepository
from infrastructure.database.models import AssetDB

logger = logging.getLogger(__name__)

class PostgresAssetRepository(IAssetRepository):
    def __init__(self, db_session: Session):
        self.db = db_session

    def find_by_id(self, asset_id: uuid.UUID) -> Optional[Asset]:
        asset_db = self.db.query(AssetDB).filter(AssetDB.id == asset_id).first()
        return Asset.from_orm(asset_db) if asset_db else None
    
    def save(self, asset: Asset) -> Asset:
        asset_db = self.db.query(AssetDB).filter(AssetDB.id == asset.id).first()
        if not asset_db:
            # This shouldn't happen in this service's workflow
            logger.error(f"Attempted to update non-existent asset with ID: {asset.id}")
            raise ValueError("Asset not found for updating")

        # Update fields
        asset_db.sca = asset.sca
        asset_db.sca_c = asset.sca_c
        asset_db.sca_i = asset.sca_i
        asset_db.sca_d = asset.sca_d
        
        self.db.commit()
        self.db.refresh(asset_db)
        return Asset.from_orm(asset_db)
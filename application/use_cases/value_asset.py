import logging

from domain.entities.asset_event import AssetDiscoveredEvent
from domain.repositories.asset_repository import IAssetRepository
from domain.repositories.messaging_producer import IMessagingProducer
from application.services.cia_calculator import CIACalculatorService

logger = logging.getLogger(__name__)

class ValueAssetUseCase:
    def __init__(
        self,
        asset_repository: IAssetRepository,
        messaging_producer: IMessagingProducer,
        cia_calculator: CIACalculatorService
    ):
        self.asset_repository = asset_repository
        self.messaging_producer = messaging_producer
        self.cia_calculator = cia_calculator

    def execute(self, event: AssetDiscoveredEvent) -> None:
        logger.info(f"Executing asset valuation for asset_id: {event.asset_id}")
        
        # 1. Retrieve the full asset record
        asset = self.asset_repository.find_by_id(event.asset_id)
        if not asset:
            logger.error(f"Asset with ID {event.asset_id} not found in database. Cannot valuate.")
            return

        # 2. Perform the calculation
        valuation_scores = self.cia_calculator.calculate_sca(asset.value)

        # 3. Update the asset entity with the new scores
        asset.sca = valuation_scores["sca"]
        asset.sca_c = valuation_scores["sca_c"]
        asset.sca_i = valuation_scores["sca_i"]
        asset.sca_d = valuation_scores["sca_d"]
        
        # 4. Save the updated asset back to the database
        updated_asset = self.asset_repository.save(asset)
        logger.info(f"Updated asset {updated_asset.id} with SCA score: {updated_asset.sca}")

        # 5. Publish the result for the next service
        self.messaging_producer.publish_asset_valuated(updated_asset)
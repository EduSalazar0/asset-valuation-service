import json
import logging
from kafka import KafkaProducer

from core.config import settings
from domain.entities.asset import Asset
from domain.repositories.messaging_producer import IMessagingProducer

logger = logging.getLogger(__name__)

class KafkaMessagingProducer(IMessagingProducer):
    # ... (constructor is identical to the previous service)

    def publish_asset_valuated(self, asset: Asset) -> None:
        # ... (error handling for producer connection)

        message = {
            "asset_id": str(asset.id),
            "scan_id": str(asset.scan_id),
            "value": asset.value,
            "sca_score": asset.sca
        }
        
        try:
            self.producer.send(settings.KAFKA_DESTINATION_TOPIC, value=message)
            self.producer.flush()
            logger.info(f"Published 'asset.valuated' event for asset_id: {asset.id}")
        except Exception as e:
            logger.error(f"Failed to publish message for asset_id {asset.id}: {e}")